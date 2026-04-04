#!/usr/bin/env python3
"""Verify governance sign-off metadata in RFC/PR markdown files."""

from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED_MARKERS = [
    "## Evidence",
    "## Sources",
]


def _matching_lines(text: str, prefix: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip().startswith(prefix)]


def check_file(path: Path, required_reviewers: tuple[str, ...] = ()) -> tuple[bool, list[str]]:
    if not path.exists():
        return False, [f"File not found: {path}"]

    text = path.read_text(encoding="utf-8")
    missing = [marker for marker in REQUIRED_MARKERS if marker not in text]
    reviewed_by = _matching_lines(text, "Reviewed-by:")
    signed_off_by = _matching_lines(text, "Signed-off-by:")

    if not reviewed_by:
        missing.append("Reviewed-by:")
    if not signed_off_by:
        missing.append("Signed-off-by:")

    if missing:
        return False, [f"Missing marker: {marker}" for marker in missing]

    for reviewer in required_reviewers:
        reviewer_present = any(reviewer.casefold() in line.casefold() for line in reviewed_by)
        if not reviewer_present:
            return False, [f"Missing required reviewer: {reviewer}"]

    return True, []


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify RFC/PR governance markers")
    parser.add_argument("path", help="Path to markdown file to validate")
    parser.add_argument(
        "--require-reviewer",
        action="append",
        default=[],
        help="Require a Reviewed-by line containing the given reviewer or role label.",
    )
    args = parser.parse_args()

    ok, errors = check_file(Path(args.path), tuple(args.require_reviewer))
    if ok:
        print("Governance approval check: PASS")
        return 0

    print("Governance approval check: FAIL")
    for err in errors:
        print(f"- {err}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
