#!/usr/bin/env python3
"""Smoke-test the packaged Python SDK import paths."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import warnings
from pathlib import Path
from textwrap import dedent
import venv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SDK_ROOT = PROJECT_ROOT / "sdk" / "python"


def _venv_python(venv_root: Path) -> Path:
    if sys.platform == "win32":
        return venv_root / "Scripts" / "python.exe"
    return venv_root / "bin" / "python"


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )


def _build_sdk_wheel(dist_dir: Path) -> Path:
    _run([sys.executable, "-m", "pip", "wheel", "--no-deps", "--wheel-dir", str(dist_dir), str(SDK_ROOT)])
    wheels = sorted(dist_dir.glob("*.whl"))
    if not wheels:
        raise SystemExit("Failed to build SDK wheel.")
    return wheels[-1]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="parva-sdk-check-") as temp_dir:
        temp_path = Path(temp_dir)
        wheel_dir = temp_path / "dist"
        wheel_dir.mkdir(parents=True, exist_ok=True)
        wheel_path = _build_sdk_wheel(wheel_dir)

        venv_root = temp_path / "venv"
        venv.EnvBuilder(with_pip=True, clear=True).create(venv_root)
        python = _venv_python(venv_root)

        _run([str(python), "-m", "pip", "install", "--upgrade", "pip"])
        _run([str(python), "-m", "pip", "install", str(wheel_path)])

        smoke_script = dedent(
            """
            import warnings

            import parva_sdk

            client = parva_sdk.ParvaClient("http://localhost:8000/v3/api")
            assert client.base_url == "http://localhost:8000/v3/api"

            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always", DeprecationWarning)
                import parva

                legacy_client = parva.ParvaClient("http://localhost:8000/v3/api")
                assert legacy_client.base_url == "http://localhost:8000/v3/api"
                assert parva.ParvaError is not None

            if not any("deprecated" in str(item.message).lower() for item in caught):
                raise SystemExit("Expected legacy 'parva' import path to emit DeprecationWarning.")
            """
        )
        _run([str(python), "-c", smoke_script])

    print(f"Python SDK package imports passed from wheel: {wheel_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
