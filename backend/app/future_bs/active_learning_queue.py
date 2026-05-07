"""Active-learning queue for future BS evidence collection."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from app.calendar.constants import BS_MONTH_NAMES

from .precomputed_store import load_precomputed_predictions
from .year_total_gate import year_total_gate

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_QUEUE_PATH = PROJECT_ROOT / "data" / "future_bs" / "corpus" / "active_learning_queue.csv"


def build_active_learning_rows(limit: int = 120) -> list[dict[str, Any]]:
    rows = []
    payload = load_precomputed_predictions()
    for year, prediction in sorted(payload.get("years", {}).items()):
        gate = year_total_gate(prediction.get("months") or [])
        for detail in prediction.get("month_details", []):
            risk_flags = set(detail.get("risk_flags") or [])
            confidence = float(detail.get("confidence_score", 0.0) or 0.0)
            if gate["valid_future_year_total"] and confidence >= 0.95 and "manual_review_recommended" not in risk_flags:
                continue
            month_number = int(detail.get("month", 1))
            rows.append(
                {
                    "priority": "P0" if not gate["valid_future_year_total"] else "P1",
                    "bs_year": int(year),
                    "month": month_number,
                    "month_name": BS_MONTH_NAMES[month_number - 1],
                    "reason": (
                        "invalid_or_exceptional_year_total"
                        if not gate["valid_future_year_total"]
                        else "low_confidence_or_manual_review"
                    ),
                    "confidence_score": confidence,
                    "risk_flags": "|".join(sorted(risk_flags)),
                    "needed_evidence": "official_panchanga_or_verified_printed_reference",
                }
            )
    return rows[:limit]


def write_active_learning_queue(path: Path = DEFAULT_QUEUE_PATH) -> list[dict[str, Any]]:
    rows = build_active_learning_rows()
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "priority",
        "bs_year",
        "month",
        "month_name",
        "reason",
        "confidence_score",
        "risk_flags",
        "needed_evidence",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return rows
