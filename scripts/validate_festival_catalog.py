#!/usr/bin/env python3
"""Validate the source festival catalog before release or CI."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _validate_rows(rows: list[dict]) -> list[str]:
    errors: list[str] = []
    ids = [row.get("id") for row in rows if isinstance(row, dict)]
    duplicate_ids = sorted(
        festival_id
        for festival_id, count in Counter(ids).items()
        if isinstance(festival_id, str) and festival_id and count > 1
    )
    if duplicate_ids:
        errors.append(f"Duplicate festival ids: {', '.join(duplicate_ids)}")

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"Festival row {index} is not an object.")
            continue
        festival_id = row.get("id")
        if not isinstance(festival_id, str) or not festival_id.strip():
            errors.append(f"Festival row {index} is missing a valid string id.")

    return errors


def main() -> int:
    festivals_path = PROJECT_ROOT / "data" / "festivals" / "festivals.json"
    payload = json.loads(festivals_path.read_text(encoding="utf-8"))
    rows = payload.get("festivals", [])
    errors = _validate_rows(rows)
    if errors:
        for error in errors:
            print(error)
        return 1

    print(f"Festival catalog valid ({len(rows)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
