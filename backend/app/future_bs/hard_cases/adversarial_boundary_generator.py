"""Generate adversarial month-start cases from corpus risk signals."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[4]
REVIEW_PATH = PROJECT_ROOT / "data" / "future_bs" / "corpus" / "human_review_queue.csv"


def generate_adversarial_boundary_cases(limit: int = 100) -> list[dict[str, Any]]:
    if not REVIEW_PATH.exists():
        return []
    with REVIEW_PATH.open(newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    selected = []
    for row in rows:
        issue = row.get("issue_type", "")
        month = int(row["bs_month"])
        if issue in {"source_disagreement", "invalid_month_length"} or month in {6, 7}:
            selected.append(
                {
                    "bs_year": int(row["bs_year"]),
                    "bs_month": month,
                    "issue_type": issue,
                    "priority": int(row["priority"]),
                    "reason": row.get("reason", ""),
                    "adversarial_tags": [
                        *("ashwin_kartik_boundary" for _ in [0] if month in {6, 7}),
                        *("source_disagreement" for _ in [0] if issue == "source_disagreement"),
                        *("fragile_year_total" for _ in [0] if issue == "invalid_month_length"),
                    ],
                }
            )
        if len(selected) >= limit:
            break
    return selected
