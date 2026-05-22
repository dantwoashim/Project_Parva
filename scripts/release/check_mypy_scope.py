#!/usr/bin/env python3
"""Report and ratchet the Python source files covered by the mypy lane."""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MIN_COVERED_PRODUCTION_FILES = 90


def _git_ls_python_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "*.py"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git ls-files failed")
    return sorted(result.stdout.splitlines())


def _load_mypy_files() -> list[str]:
    payload = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    files = payload.get("tool", {}).get("mypy", {}).get("files", [])
    if not isinstance(files, list) or not all(isinstance(item, str) for item in files):
        raise RuntimeError("pyproject.toml [tool.mypy].files must be a list of strings")
    return files


def _is_production_python(path: str) -> bool:
    if path.startswith(("tests/", "backend/tests/")):
        return False
    if "/tests/" in path or path.endswith("_test.py"):
        return False
    if "__pycache__" in path or "/build/" in path:
        return False
    return path.startswith(("backend/", "scripts/", "packages/", "sdk/", "tools/"))


def _covered_by_mypy(path: str, entries: list[str]) -> bool:
    for entry in entries:
        normalized = entry.rstrip("/")
        if path == normalized:
            return True
        if path.startswith(normalized + "/"):
            return True
    return False


def build_scope_report() -> dict[str, Any]:
    tracked_python = _git_ls_python_files()
    production_python = [path for path in tracked_python if _is_production_python(path)]
    mypy_entries = _load_mypy_files()
    covered = [path for path in production_python if _covered_by_mypy(path, mypy_entries)]
    uncovered = [path for path in production_python if path not in set(covered)]
    return {
        "schema": "parva-mypy-scope-v1",
        "tracked_python_files": len(tracked_python),
        "production_python_files": len(production_python),
        "mypy_configured_entries": mypy_entries,
        "covered_production_files": len(covered),
        "uncovered_production_files": len(uncovered),
        "covered_production_ratio": round(len(covered) / len(production_python), 4)
        if production_python
        else 1.0,
        "minimum_covered_production_files": MIN_COVERED_PRODUCTION_FILES,
        "uncovered_examples": uncovered[:25],
    }


def main() -> int:
    report = build_scope_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["covered_production_files"] < MIN_COVERED_PRODUCTION_FILES:
        print(
            "mypy scope regression: covered production files below ratchet "
            f"{MIN_COVERED_PRODUCTION_FILES}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
