#!/usr/bin/env python3
"""Create a clean source archive for release distribution."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

if sys.version_info < (3, 11):  # pragma: no cover - script is pinned to 3.11 in docs
    raise SystemExit("package_source_archive.py requires Python 3.11+")

import tomllib

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"
DIST_DIR = PROJECT_ROOT / "dist"

EXCLUDED_DIR_NAMES = {
    ".git",
    ".venv",
    ".venv311",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
    "node_modules",
    ".vite",
    "dist",
    "output",
    "reports",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".zip"}
EXCLUDED_RELATIVE_PREFIXES = {
    Path("benchmark/results"),
    Path("backend/project_parva.egg-info"),
}
EXCLUDED_RELATIVE_PATHS = {
    Path("backend/data/webhooks/subscriptions.json"),
}


def _project_version() -> str:
    payload = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    return str(payload["project"]["version"])


def _should_skip(path: Path) -> bool:
    relative = path.relative_to(PROJECT_ROOT)

    if any(part in EXCLUDED_DIR_NAMES for part in relative.parts):
        return True

    if any(part.startswith(".verify") for part in relative.parts):
        return True

    if any(relative == prefix or prefix in relative.parents for prefix in EXCLUDED_RELATIVE_PREFIXES):
        return True

    if relative in EXCLUDED_RELATIVE_PATHS:
        return True

    if path.suffix in EXCLUDED_SUFFIXES:
        return True

    return False


def main() -> int:
    version = _project_version()
    archive_root = f"project-parva-{version}"
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    archive_path = DIST_DIR / f"{archive_root}-source.zip"

    files_written = 0
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(PROJECT_ROOT.rglob("*")):
            if not path.is_file() or _should_skip(path):
                continue
            relative = path.relative_to(PROJECT_ROOT)
            archive.write(path, arcname=str(Path(archive_root) / relative))
            files_written += 1

    print(f"Wrote {archive_path} ({files_written} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
