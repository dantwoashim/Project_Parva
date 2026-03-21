#!/usr/bin/env python3
"""Verify the supported local toolchain before deeper Parva validation runs."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from node_runtime import current_npm_version, resolve_node_runtime

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = PROJECT_ROOT / "frontend"


def _check_python() -> tuple[bool, str]:
    if sys.version_info[:2] != (3, 11):
        return False, f"Expected Python 3.11.x, found {sys.version.split()[0]}"
    return True, f"Python {sys.version.split()[0]}"


def _run_version_command(command: list[str]) -> tuple[bool, str]:
    executable = shutil.which(command[0])
    if not executable:
        return False, f"{command[0]} not found"

    resolved_command = [executable, *command[1:]]
    result = subprocess.run(
        resolved_command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip() or "command failed"
        return False, stderr
    return True, result.stdout.strip()


def _check_node() -> tuple[bool, str]:
    runtime = resolve_node_runtime()
    if not runtime:
        ok, detail = _run_version_command(["node", "--version"])
        if ok:
            version = detail.removeprefix("v")
            return False, f"Expected Node 20.x, found v{version}"
        return False, "Unable to resolve Node 20.x from system PATH or managed fallback."
    return True, runtime.describe()


def _check_npm() -> tuple[bool, str]:
    runtime = resolve_node_runtime()
    return current_npm_version(runtime)


def _check_frontend_lockfile() -> tuple[bool, str]:
    lockfile = FRONTEND_DIR / "package-lock.json"
    if not lockfile.exists():
        return False, f"Missing frontend lockfile: {lockfile}"
    return True, str(lockfile.relative_to(PROJECT_ROOT))


def main() -> int:
    checks = {
        "python": _check_python(),
        "node": _check_node(),
        "npm": _check_npm(),
        "frontend_lockfile": _check_frontend_lockfile(),
    }
    payload = {
        "ok": all(result for result, _ in checks.values()),
        "checks": {
            name: {"ok": ok, "detail": detail}
            for name, (ok, detail) in checks.items()
        },
    }
    print(json.dumps(payload, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
