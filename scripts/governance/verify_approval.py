#!/usr/bin/env python3
"""Verify governance sign-off metadata in RFC/PR markdown files."""

from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED_MARKERS = [
    "## Evidence",
    "## Sources",
    "Reviewed-by:",
    "Signed-off-by:",
]


def check_file(path: Path) -> tuple[bool, list[str]]:
    if not path.exists():
        return False, [f"File not found: {path}"]

    text = path.read_text(encoding="utf-8")
    missing = [marker for marker in REQUIRED_MARKERS if marker not in text]
    if missing:
        return False, [f"Missing marker: {marker}" for marker in missing]

    return True, []


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify RFC/PR governance markers")
    parser.add_argument("path", help="Path to markdown file to validate")
    args = parser.parse_args()

    ok, errors = check_file(Path(args.path))
    if ok:
        print("Governance approval check: PASS")
        return 0

    print("Governance approval check: FAIL")
    for err in errors:
        print(f"- {err}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
