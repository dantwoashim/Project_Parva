"""Build the month-start corpus from reconstructed CSV artifacts."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .month_start_record import MonthStartRecord

PROJECT_ROOT = Path(__file__).resolve().parents[4]
STARTS_PATH = PROJECT_ROOT / "data" / "future_bs" / "corpus" / "reconstructed_month_starts.csv"
PUBLICATION_STATUS = "computed_prediction_not_official"


def build_month_start_corpus(path: Path = STARTS_PATH) -> dict[str, Any]:
    rows = []
    if path.exists():
        with path.open(newline="", encoding="utf-8-sig") as fh:
            for raw in csv.DictReader(fh):
                record = MonthStartRecord(
                    bs_year=int(raw["bs_year"]),
                    bs_month=int(raw["bs_month"]),
                    month_start_ad=raw["month_start_ad"],
                    witness_count=int(raw["witness_count"]),
                    best_source_tier=int(raw["best_source_tier"]),
                    agreement_score=float(raw["agreement_score"]),
                    verification_status=raw["verification_status"],
                    manual_review_required=raw.get("manual_review_required") == "true",
                )
                rows.append(record.payload())
    return {
        "publication_status": PUBLICATION_STATUS,
        "primitive": "month_start_ad",
        "case_count": len(rows),
        "records": rows,
    }
