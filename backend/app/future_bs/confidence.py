"""Confidence scoring for future BS month-length predictions."""

from __future__ import annotations


def confidence_label(score: float, *, known_official: bool = False) -> str:
    if known_official:
        return "official_verified"
    if score >= 0.95:
        return "computed_very_high"
    if score >= 0.85:
        return "computed_high"
    if score >= 0.70:
        return "computed_medium"
    if score >= 0.55:
        return "computed_low"
    return "needs_review"


def horizon_factor(bs_year: int, corpus_max_year: int) -> float:
    if bs_year <= corpus_max_year:
        return 1.0
    distance = bs_year - corpus_max_year
    if distance <= 10:
        return 0.94
    if distance <= 25:
        return 0.88
    if distance <= 50:
        return 0.80
    if distance <= 75:
        return 0.72
    return 0.62


def score_confidence(
    *,
    max_probability: float,
    model_agreement_ratio: float,
    source_quality: float,
    boundary_factor: float,
    future_horizon_factor: float,
) -> float:
    score = (
        max_probability * 0.42
        + model_agreement_ratio * 0.24
        + source_quality * 0.14
        + boundary_factor * 0.10
        + future_horizon_factor * 0.10
    )
    return round(max(0.0, min(score, 1.0)), 4)
