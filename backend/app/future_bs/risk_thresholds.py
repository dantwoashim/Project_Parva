"""Risk threshold helpers tuned for false-confidence control."""

from __future__ import annotations

from typing import Any

DEFAULT_RISK_THRESHOLDS = {
    "green_min_probability": 0.985,
    "green_max_flip_rate": 0.01,
    "green_max_prediction_set_95_width": 1,
    "green_requires_valid_year_total": True,
    "yellow_max_prediction_set_95_width": 2,
}


def classify_prediction_risk(
    detail: dict[str, Any],
    *,
    prediction_set_95: list[int] | None = None,
    flip_rate: float = 0.0,
    year_total_valid: bool = True,
    thresholds: dict[str, Any] | None = None,
) -> str:
    cfg = {**DEFAULT_RISK_THRESHOLDS, **(thresholds or {})}
    risk_flags = set(detail.get("risk_flags") or [])
    if cfg["green_requires_valid_year_total"] and not year_total_valid:
        return "RED"
    if "manual_review_recommended" in risk_flags or "constraint_violation" in risk_flags:
        return "YELLOW"
    set_width = len(prediction_set_95 or [])
    if set_width >= 3:
        return "RED"
    if flip_rate > 0.15:
        return "RED"
    if (
        float(detail.get("confidence_score", 0.0) or 0.0) >= float(cfg["green_min_probability"])
        and flip_rate <= float(cfg["green_max_flip_rate"])
        and set_width <= int(cfg["green_max_prediction_set_95_width"])
    ):
        return "GREEN"
    return "YELLOW" if set_width <= int(cfg["yellow_max_prediction_set_95_width"]) else "RED"
