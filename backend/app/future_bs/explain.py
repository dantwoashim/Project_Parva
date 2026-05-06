"""Explanation engine for future BS month-length predictions."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.calendar.constants import BS_MONTH_NAMES


def explain_prediction_month(prediction: dict[str, Any], month: int) -> dict[str, Any]:
    if month < 1 or month > 12:
        raise ValueError("month must be between 1 and 12.")
    detail = prediction["month_details"][month - 1]
    votes: Counter[str] = Counter()
    computational_days = detail.get("computational_days")
    legacy_days = detail.get("legacy_days")
    if computational_days is not None:
        votes[str(computational_days)] += 1
    if legacy_days is not None:
        votes[str(legacy_days)] += 1
    if not votes:
        votes[str(detail["final_days"])] = 1
    boundary_risk = "high" if "sankranti_near_civil_assignment_boundary" in detail.get("risk_flags", []) else "low"
    if "manual_review_recommended" in detail.get("risk_flags", []):
        recommendation = "Manual review recommended before financial-contract use."
    else:
        recommendation = "No model-level manual review flag for this month."
    return {
        "bs_year": prediction["bs_year"],
        "month": month,
        "month_name": BS_MONTH_NAMES[month - 1],
        "final_days": detail["final_days"],
        "confidence": detail["confidence_label"],
        "confidence_score": detail["confidence_score"],
        "reasoning": {
            "model_votes": dict(votes),
            "boundary_risk": boundary_risk,
            "historical_similar_case_accuracy": detail.get("historical_similar_case_accuracy"),
            "main_risk": "civil_date_assignment_boundary"
            if "manual_review_recommended" in detail.get("risk_flags", [])
            else "none",
        },
        "recommendation": recommendation,
    }
