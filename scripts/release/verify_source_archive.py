#!/usr/bin/env python3
"""Verify that the release source archive contains only source material."""

from __future__ import annotations

import argparse
import tomllib
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"
DIST_DIR = PROJECT_ROOT / "dist"

COMPILED_OR_LOCAL_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".venv311",
    ".verify",
    "__pycache__",
    "dist",
    "htmlcov",
    "node_modules",
    "output",
    "reports",
}
COMPILED_OR_LOCAL_SUFFIXES = {
    ".DS_Store",
    ".log",
    ".pyc",
    ".pyo",
    ".sqlite",
    ".zip",
}
COMPILED_OR_LOCAL_PREFIXES = (
    "backend/data/snapshots/",
    "backend/data/traces/",
    "frontend/dist/",
    "sdk/python/build/",
)


def _project_version() -> str:
    payload = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    return str(payload["project"]["version"])


def _default_archive_path() -> Path:
    version = _project_version()
    preferred = DIST_DIR / f"project-parva-{version}-source.zip"
    if preferred.exists():
        return preferred

    candidates = sorted(DIST_DIR.glob("*-source.zip"), key=lambda path: path.stat().st_mtime)
    if candidates:
        return candidates[-1]
    raise SystemExit(
        f"No source archive found in {DIST_DIR}. Run scripts/release/package_source_archive.py first."
    )


def _normalized_members(archive_path: Path) -> list[str]:
    """Return archive member paths without the generated top-level archive root."""
    with zipfile.ZipFile(archive_path) as archive:
        names = [
            name.rstrip("/")
            for name in archive.namelist()
            if name and not name.endswith("/")
        ]

    if not names:
        return []

    first_parts = {name.split("/", 1)[0] for name in names}
    if len(first_parts) == 1 and all("/" in name for name in names):
        return sorted(name.split("/", 1)[1] for name in names)
    return sorted(names)


def _member_failure(member: str) -> str | None:
    normalized = member.strip().lstrip("/")
    parts = normalized.split("/")

    if any(part.endswith(".egg-info") for part in parts):
        return f"archive contains packaging residue: {normalized}"

    if any(part in COMPILED_OR_LOCAL_PARTS for part in parts):
        return f"archive contains compiled/local artifact: {normalized}"

    if any(normalized.startswith(prefix) for prefix in COMPILED_OR_LOCAL_PREFIXES):
        return f"archive contains compiled/local artifact: {normalized}"

    if any(normalized.endswith(suffix) for suffix in COMPILED_OR_LOCAL_SUFFIXES):
        return f"archive contains compiled/local artifact: {normalized}"

    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "archive",
        nargs="?",
        type=Path,
        help="Archive to verify. Defaults to dist/project-parva-<version>-source.zip.",
    )
    args = parser.parse_args(argv)

    archive_path = (args.archive or _default_archive_path()).resolve()
    if not archive_path.exists():
        raise SystemExit(f"Archive does not exist: {archive_path}")

    failures = [
        failure
        for member in _normalized_members(archive_path)
        if (failure := _member_failure(member))
    ]

    if failures:
        for failure in failures:
            print(f"[source-archive] {failure}")
        return 1

    print(f"Source archive verified: {archive_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
