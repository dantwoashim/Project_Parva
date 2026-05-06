#!/usr/bin/env python3
"""Validate a source-labeled future BS corpus CSV."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

MONTH_COLUMNS = [
    "baishakh",
    "jestha",
    "ashadh",
    "shrawan",
    "bhadra",
    "ashwin",
    "kartik",
    "mangsir",
    "poush",
    "magh",
    "falgun",
    "chaitra",
]


def validate(path: Path) -> dict:
    rows = 0
    issues: list[str] = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            rows += 1
            year = raw.get("bs_year", "?")
            try:
                months = [int(raw[column]) for column in MONTH_COLUMNS]
            except (KeyError, ValueError) as exc:
                issues.append(f"{year}: invalid month columns ({exc})")
                continue
            if len(months) != 12 or any(days < 29 or days > 32 for days in months):
                issues.append(f"{year}: month lengths must be 29-32 days")
            if not raw.get("source_type") or not raw.get("verification_status"):
                issues.append(f"{year}: source_type and verification_status are required")
    return {"rows": rows, "issues": issues, "ok": not issues}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    result = validate(args.path)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
