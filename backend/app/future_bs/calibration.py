"""Calibration summaries for future BS model families."""

from __future__ import annotations

from typing import Any

from app.calendar.constants import BS_MAX_YEAR, BS_MIN_YEAR

from .solar_ingress_predictor import calibrated_rule_weights


def calibration_summary(train_start: int = BS_MIN_YEAR, train_end: int = BS_MAX_YEAR) -> dict[str, Any]:
    weights = calibrated_rule_weights(train_start, train_end)
    return {
        "train_range": f"{train_start}-{train_end} BS",
        "rule_weights_percent": {name: round(weight * 100, 2) for name, weight in weights.items()},
        "selected_family": "solar_ingress_civil_rule_ensemble",
        "status": "calibrated_against_source_labeled_corpus",
    }
