"""Lightweight perturbation robustness scoring for month predictions."""

from __future__ import annotations

from typing import Any

from .prediction_sets import normalize_probability_keys


def perturbation_payload(detail: dict[str, Any]) -> dict[str, Any]:
    probabilities = normalize_probability_keys(detail.get("probability") or {})
    ranked = sorted(probabilities.values(), reverse=True)
    top = ranked[0] if ranked else 0.0
    second = ranked[1] if len(ranked) > 1 else 0.0
    risk_flags = set(detail.get("risk_flags") or [])
    disagreement = 1.0 if detail.get("model_agreement") == "1/2" else 0.0
    review_penalty = 0.12 if "manual_review_recommended" in risk_flags else 0.0
    flip_rate = max(0.0, min(1.0, second + review_penalty + disagreement * 0.08))
    return {
        "flip_rate": round(flip_rate, 4),
        "stable": flip_rate < 0.05 and top >= 0.95,
        "probability_margin": round(max(0.0, top - second), 4),
        "method": "probability_margin_plus_disagreement_proxy_v1",
    }
