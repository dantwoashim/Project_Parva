"""Decode reconstructed month starts through year-total lattice constraints."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

from app.research.future_bs.paths import project_root

from .lattice_constraints import valid_year_total

PROJECT_ROOT = project_root()
LENGTHS_PATH = PROJECT_ROOT / "data" / "future_bs" / "corpus" / "reconstructed_month_lengths.csv"
PUBLICATION_STATUS = "computed_prediction_not_official"


def decode_month_start_lattice(path: Path = LENGTHS_PATH) -> dict[str, Any]:
    rows = []
    if path.exists():
        with path.open(newline="", encoding="utf-8-sig") as fh:
            rows = list(csv.DictReader(fh))
    by_year: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_year[int(row["bs_year"])].append(row)
    decoded = []
    invalid_years = []
    for year in sorted(by_year):
        months = sorted(by_year[year], key=lambda row: int(row["bs_month"]))
        total = sum(int(row["month_length"]) for row in months)
        valid = len(months) == 12 and valid_year_total(total)
        payload = {
            "bs_year": year,
            "month_count": len(months),
            "decoded_total": total,
            "valid": valid,
            "claimable": valid and all(row.get("verification_status") != "manual_review_required" for row in months),
            "risk_label": "GREEN" if valid else "RED",
            "reason": "valid_year_total" if valid else "invalid_or_exceptional_year_total",
        }
        decoded.append(payload)
        if not valid:
            invalid_years.append(payload)
    return {
        "publication_status": PUBLICATION_STATUS,
        "decoder": "month_start_lattice_v1",
        "year_count": len(decoded),
        "invalid_year_count": len(invalid_years),
        "invalid_years": invalid_years,
        "years": decoded,
    }
