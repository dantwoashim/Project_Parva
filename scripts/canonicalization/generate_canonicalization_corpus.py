#!/usr/bin/env python3
"""Generate the Phase 03 canonicalization equivalence corpus."""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT = PROJECT_ROOT / "tests" / "fixtures" / "canonicalization_equivalence.json"


def _devanagari_digits(value: int) -> str:
    mapping = str.maketrans("0123456789", "०१२३४५६७८९")
    return str(value).translate(mapping)


def _equivalent_pairs() -> list[list[dict[str, object]]]:
    pairs: list[list[dict[str, object]]] = []
    for index in range(25):
        year = 2082 + (index % 3)
        pairs.append(
            [
                {
                    "operation": "find_festival_date",
                    "input": {"festival": "दशैं", "year": _devanagari_digits(year)},
                },
                {
                    "operation": " find_festival_date ",
                    "input": {"festival": "DASAIN", "year": str(year)},
                    "context": {"calendar": "bs", "place_id": "np:national:default"},
                },
            ]
        )
    for day in range(1, 26):
        date_value = f"2082-01-{day:02d}"
        pairs.append(
            [
                {"operation": "check_working_day", "input": {"date": date_value}},
                {
                    "operation": "CHECK_WORKING_DAY",
                    "input": {"date": f" {date_value} "},
                    "context": {
                        "calendar": "BS",
                        "timezone": "Asia/Kathmandu",
                        "policy_id": "canonical@0.1.0",
                    },
                },
            ]
        )
    return pairs


def _different_pairs() -> list[list[dict[str, object]]]:
    pairs: list[list[dict[str, object]]] = []
    for day in range(1, 26):
        date_value = f"2082-01-{day:02d}"
        pairs.append(
            [
                {
                    "operation": "check_working_day",
                    "input": {"date": date_value},
                    "context": {"policy_id": "canonical@0.1.0"},
                },
                {
                    "operation": "check_working_day",
                    "input": {"date": date_value},
                    "context": {"policy_id": "banking_review_required@0.1.0"},
                },
            ]
        )
    for day in range(1, 26):
        date_value = f"2082-01-{day:02d}"
        pairs.append(
            [
                {
                    "operation": "check_working_day",
                    "input": {"date": date_value},
                    "context": {"place_id": "np:national:default"},
                },
                {
                    "operation": "check_working_day",
                    "input": {"date": date_value},
                    "context": {"place_id": "np:kathmandu:local"},
                },
            ]
        )
    return pairs


def main() -> int:
    payload = {
        "equivalent": _equivalent_pairs(),
        "different": _different_pairs(),
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(payload['equivalent'])} equivalent and {len(payload['different'])} different pairs to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
