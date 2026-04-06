#!/usr/bin/env python3
"""Verify that a generated source archive excludes non-source artifacts."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DIST_DIR = PROJECT_ROOT / "dist"
DISALLOWED_SEGMENTS = {
    ".venv",
    "node_modules",
    "dist",
    "output",
    "reports",
}
DISALLOWED_PATHS = {
    "evaluation.csv",
}


def _default_archive() -> Path:
    candidates = sorted(DIST_DIR.glob("*-source.zip"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not candidates:
        raise SystemExit("No source archive found in dist/. Run package_source_archive.py first.")
    return candidates[0]


def _normalized_members(archive_path: Path) -> list[str]:
    with zipfile.ZipFile(archive_path) as archive:
        names = [name.rstrip("/") for name in archive.namelist() if name and not name.endswith("/")]
    if not names:
        raise SystemExit(f"Archive is empty: {archive_path}")

    root_prefix = names[0].split("/", 1)[0]
    normalized: list[str] = []
    for name in names:
        if name == root_prefix:
            continue
        normalized.append(name.split("/", 1)[1] if name.startswith(f"{root_prefix}/") else name)
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, help="Path to a source zip archive. Defaults to the newest dist/*-source.zip")
    args = parser.parse_args()

    archive_path = args.archive or _default_archive()
    members = _normalized_members(archive_path)
    failures: list[str] = []

    for member in members:
        if member in DISALLOWED_PATHS:
            failures.append(f"archive contains generated artifact: {member}")
            continue
        parts = Path(member).parts
        if any(part in DISALLOWED_SEGMENTS for part in parts):
            failures.append(f"archive contains disallowed path: {member}")

    if failures:
        print("\n".join(failures))
        return 1

    print(f"Source archive verified: {archive_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
