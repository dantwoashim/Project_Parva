"""Explainable decision-surface scoring for hidden calendar rules."""

from __future__ import annotations

from typing import Any

PUBLICATION_STATUS = "computed_prediction_not_official"


def score_decision_surfaces(features: list[dict[str, Any]]) -> list[dict[str, Any]]:
    total = len(features) or 1
    valid = sum(1 for row in features if int(row["month_length"]) in {29, 30, 31, 32})
    boundary = sum(1 for row in features if row.get("boundary_sensitive_month"))
    return [
        {
            "program": "source_weighted_month_start_consensus",
            "validity_rate": round(valid / total, 6),
            "boundary_cases": boundary,
            "complexity": 1,
            "selected": True,
        },
        {
            "program": "month_mode_baseline",
            "validity_rate": round(valid / total, 6),
            "boundary_cases": boundary,
            "complexity": 2,
            "selected": False,
        },
    ]
