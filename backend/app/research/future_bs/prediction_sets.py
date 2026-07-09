"""Prediction-set helpers for calendar model-risk responses."""

from __future__ import annotations

from typing import Any

from .models import MONTH_DAY_VALUES

MIN_OFFICIAL_CLAIM_CASES = 528


def normalize_probability_keys(probability: dict[str, float]) -> dict[str, float]:
    normalized: dict[str, float] = {}
    for days in MONTH_DAY_VALUES:
        normalized[str(days)] = float(
            probability.get(str(days), probability.get(f"{days}_days", 0.0))
        )
    total = sum(normalized.values())
    if total <= 0:
        return {str(days): 1.0 if days == 30 else 0.0 for days in MONTH_DAY_VALUES}
    return {key: round(value / total, 6) for key, value in normalized.items()}


def prediction_set(probability: dict[str, float], coverage: float) -> list[int]:
    normalized = normalize_probability_keys(probability)
    ranked = sorted(
        ((int(days), prob) for days, prob in normalized.items()),
        key=lambda item: (-item[1], item[0]),
    )
    selected: list[int] = []
    cumulative = 0.0
    for days, prob in ranked:
        if prob <= 0 and selected:
            continue
        selected.append(days)
        cumulative += prob
        if cumulative >= coverage:
            break
    return sorted(selected)


def prediction_set_payload(detail: dict[str, Any]) -> dict[str, Any]:
    probability = normalize_probability_keys(detail.get("probability") or {})
    official_cases = int(detail.get("calibration_official_cases", 0) or 0)
    coverage_claim_ready = official_cases >= MIN_OFFICIAL_CLAIM_CASES
    return {
        "probabilities": probability,
        "prediction_set_80": prediction_set(probability, 0.80),
        "prediction_set_95": prediction_set(probability, 0.95),
        "coverage_method": (
            "split_conformal_if_available"
            if coverage_claim_ready
            else "calibrated_probability_set"
        ),
        "coverage_claim_ready": coverage_claim_ready,
        "coverage_claim_reason": (
            "sufficient_official_cases"
            if coverage_claim_ready
            else "insufficient_official_cases"
        ),
        "point_prediction_claimable": (
            len(prediction_set(probability, 0.95)) == 1
            and float(detail.get("confidence_score", 0.0)) >= 0.95
            and "manual_review_recommended" not in set(detail.get("risk_flags") or [])
            and coverage_claim_ready
        ),
    }
