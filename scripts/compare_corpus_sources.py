#!/usr/bin/env python3
"""Compare two source-labeled BS month-length corpus files month by month."""

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


def load(path: Path) -> dict[int, list[int]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return {
            int(row["bs_year"]): [int(row[column]) for column in MONTH_COLUMNS]
            for row in csv.DictReader(fh)
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    args = parser.parse_args()
    left = load(args.left)
    right = load(args.right)
    mismatches = []
    for year in sorted(set(left) & set(right)):
        for index, (left_days, right_days) in enumerate(zip(left[year], right[year]), start=1):
            if left_days != right_days:
                mismatches.append(
                    {
                        "bs_year": year,
                        "month": index,
                        "left_days": left_days,
                        "right_days": right_days,
                    }
                )
    payload = {
        "left": str(args.left),
        "right": str(args.right),
        "years_compared": len(set(left) & set(right)),
        "months_compared": len(set(left) & set(right)) * 12,
        "mismatches": len(mismatches),
        "mismatch_details": mismatches,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if not mismatches else 1


if __name__ == "__main__":
    raise SystemExit(main())
