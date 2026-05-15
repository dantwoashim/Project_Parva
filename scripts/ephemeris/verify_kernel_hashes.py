#!/usr/bin/env python3
"""Verify optional JPL/NAIF ephemeris kernel hashes without leaking paths."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config" / "ephemeris-kernels.yaml"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _kernel_path(kernel: dict[str, Any], *, project_root: Path = PROJECT_ROOT) -> Path | None:
    env_var = str(kernel.get("path_env_var") or "")
    configured = os.getenv(env_var, "").strip() if env_var else ""
    if configured:
        return Path(configured).expanduser()

    defaults = {
        "PARVA_JPL_DE440_KERNEL": project_root / "data" / "ephemeris" / "jpl" / "de440.bsp",
        "PARVA_JPL_DE441_PART1_KERNEL": project_root / "data" / "ephemeris" / "jpl" / "de441_part-1.bsp",
        "PARVA_JPL_DE441_PART2_KERNEL": project_root / "data" / "ephemeris" / "jpl" / "de441_part-2.bsp",
    }
    return defaults.get(env_var)


def verify(config_path: Path = CONFIG_PATH, *, project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    results: list[dict[str, Any]] = []
    ok = True

    for kernel in config.get("kernels", []):
        kernel_id = str(kernel.get("id") or "unknown")
        expected = kernel.get("expected_sha256")
        path = _kernel_path(kernel, project_root=project_root)
        present = bool(path and path.exists())
        row: dict[str, Any] = {
            "id": kernel_id,
            "env_var": kernel.get("path_env_var"),
            "present": present,
            "public_runtime_required": bool(kernel.get("public_runtime_required")),
            "private_or_research": bool(kernel.get("private_or_research")),
        }

        if not present:
            row["status"] = "skipped_absent_optional_kernel"
        elif not expected:
            row["status"] = "blocked_present_without_expected_hash"
            ok = False
        else:
            actual = _sha256(path)
            row["status"] = "pass" if actual == str(expected).lower() else "fail_hash_mismatch"
            row["sha256"] = actual
            ok = ok and row["status"] == "pass"
        results.append(row)

    return {
        "ok": ok,
        "config": "config/ephemeris-kernels.yaml" if config_path == CONFIG_PATH else config_path.name,
        "results": results,
        "path_policy": "local kernel paths intentionally omitted",
    }


def main() -> int:
    result = verify()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
