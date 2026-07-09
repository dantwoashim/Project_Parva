"""Feature extraction for month-start model/risk analysis."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from app.research.future_bs.paths import project_root

PROJECT_ROOT = project_root()
LENGTHS_PATH = PROJECT_ROOT / "data" / "future_bs" / "corpus" / "reconstructed_month_lengths.csv"
PUBLICATION_STATUS = "computed_prediction_not_official"


def build_month_start_features(path: Path = LENGTHS_PATH) -> dict[str, Any]:
    rows = []
    raw_rows = []
    if path.exists():
        with path.open(newline="", encoding="utf-8-sig") as fh:
            raw_rows = list(csv.DictReader(fh))
    by_key = {(int(row["bs_year"]), int(row["bs_month"])): row for row in raw_rows}
    for row in raw_rows:
        year = int(row["bs_year"])
        month = int(row["bs_month"])
        previous = by_key.get((year, month - 1)) if month > 1 else by_key.get((year - 1, 12))
        next_row = by_key.get((year, month + 1)) if month < 12 else by_key.get((year + 1, 1))
        rows.append(
            {
                "bs_year": year,
                "bs_month": month,
                "month_start_ad": row["month_start_ad"],
                "month_length": int(row["month_length"]),
                "previous_month_length": int(previous["month_length"]) if previous else None,
                "next_month_length": int(next_row["month_length"]) if next_row else None,
                "year_mod_19": year % 19,
                "year_mod_28": year % 28,
                "year_mod_57": year % 57,
                "best_source_tier": int(row["best_source_tier"]),
                "agreement_score": float(row["agreement_score"]),
                "manual_review_required": row["verification_status"] == "manual_review_required",
                "boundary_sensitive_month": month in {6, 7, 12, 1},
            }
        )
    return {
        "publication_status": PUBLICATION_STATUS,
        "feature_count": len(rows),
        "features": rows,
    }
