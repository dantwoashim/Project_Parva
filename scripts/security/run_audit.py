#!/usr/bin/env python3
"""Run lightweight security checks (dependency + config) and emit report."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import tomllib
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = PROJECT_ROOT / "reports" / "security_audit.json"
BACKEND_PYPROJECT = PROJECT_ROOT / "pyproject.toml"
SDK_PYPROJECT = PROJECT_ROOT / "sdk" / "python" / "pyproject.toml"


def _run(cmd: list[str], cwd: Path) -> dict:
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
        return {
            "cmd": " ".join(cmd),
            "returncode": proc.returncode,
            "stdout": proc.stdout[-8000:],
            "stderr": proc.stderr[-8000:],
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "cmd": " ".join(cmd),
            "returncode": -1,
            "stdout": "",
            "stderr": str(exc),
        }


def _project_requirements_from_pyproject(path: Path) -> list[str]:
    if not path.exists():
        return []
    payload = tomllib.loads(path.read_text(encoding="utf-8"))
    project = payload.get("project", {})
    dependencies = project.get("dependencies", [])
    return [str(item).strip() for item in dependencies if str(item).strip()]


def main() -> int:
    checks = []
    npm_binary = shutil.which("npm.cmd") or shutil.which("npm")

    # Python dependency check
    if importlib.util.find_spec("pip_audit") is not None:
        python_requirements = []
        for pyproject in (BACKEND_PYPROJECT, SDK_PYPROJECT):
            python_requirements.extend(_project_requirements_from_pyproject(pyproject))
        deduped_requirements = list(dict.fromkeys(python_requirements))

        if deduped_requirements:
            with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as handle:
                handle.write("\n".join(deduped_requirements) + "\n")
                requirements_path = Path(handle.name)
            try:
                checks.append(
                    (
                        "pip_audit",
                        _run(
                            [sys.executable, "-m", "pip_audit", "-r", str(requirements_path), "-f", "json"],
                            PROJECT_ROOT,
                        ),
                    )
                )
            finally:
                requirements_path.unlink(missing_ok=True)
        else:
            checks.append(
                (
                    "pip_audit",
                    {
                        "cmd": f"{sys.executable} -m pip_audit",
                        "returncode": None,
                        "stdout": "",
                        "stderr": "No Python project dependencies found; skipped",
                    },
                )
            )
    else:
        checks.append(
            (
                "pip_audit",
                {
                    "cmd": f"{sys.executable} -m pip_audit -f json",
                    "returncode": None,
                    "stdout": "",
                    "stderr": "pip-audit not installed; skipped",
                },
            )
        )

    # Node dependency check
    if npm_binary:
        checks.append(("npm_audit", _run([npm_binary, "audit", "--omit=dev", "--json"], PROJECT_ROOT / "frontend")))
    else:
        checks.append(
            (
                "npm_audit",
                {
                    "cmd": "npm audit --json",
                    "returncode": None,
                    "stdout": "",
                    "stderr": "npm not installed; skipped",
                },
            )
        )

    failing_checks = [
        name
        for name, result in checks
        if result.get("returncode") not in {0, None}
    ]
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "failed" if failing_checks else "passed",
        "summary": {
            "check_count": len(checks),
            "failing_checks": failing_checks,
        },
        "checks": {name: result for name, result in checks},
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(REPORT_PATH)}, indent=2))

    return 1 if failing_checks else 0


if __name__ == "__main__":
    raise SystemExit(main())
