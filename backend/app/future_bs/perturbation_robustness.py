"""Lightweight perturbation robustness scoring for month predictions."""

from __future__ import annotations

from typing import Any

from .prediction_sets import normalize_probability_keys


def _entropy_penalty(committee: dict[str, Any] | None) -> float:
    if not committee:
        return 0.04
    entropy = float(committee.get("rule_entropy", 0.0) or 0.0)
    return min(0.18, entropy * 0.16)


def _merge_probabilities(
    base: dict[str, float],
    precedent: dict[str, Any] | None,
) -> dict[str, float]:
    if not precedent:
        return base
    precedent_probs = normalize_probability_keys(precedent.get("precedent_probabilities") or {})
    merged = {
        key: (base.get(key, 0.0) * 0.72) + (precedent_probs.get(key, 0.0) * 0.28)
        for key in base
    }
    return normalize_probability_keys(merged)


def perturbation_payload(
    detail: dict[str, Any],
    *,
    committee: dict[str, Any] | None = None,
    precedent: dict[str, Any] | None = None,
    scenario_count: int = 64,
) -> dict[str, Any]:
    probabilities = normalize_probability_keys(detail.get("probability") or {})
    scenario_probabilities = _merge_probabilities(probabilities, precedent)
    ranked = sorted(probabilities.values(), reverse=True)
    top = ranked[0] if ranked else 0.0
    second = ranked[1] if len(ranked) > 1 else 0.0
    risk_flags = set(detail.get("risk_flags") or [])
    disagreement = 1.0 if detail.get("model_agreement") == "1/2" else 0.0
    boundary = 1.0 if any("boundary" in flag or "cutoff" in flag for flag in risk_flags) else 0.0
    review_penalty = 0.12 if "manual_review_recommended" in risk_flags else 0.0
    flip_rate = max(
        0.0,
        min(
            1.0,
            second
            + review_penalty
            + disagreement * 0.08
            + boundary * 0.05
            + _entropy_penalty(committee),
        ),
    )
    scenario_votes = {
        days: int(round(probability * scenario_count))
        for days, probability in scenario_probabilities.items()
        if probability > 0
    }
    missing = scenario_count - sum(scenario_votes.values())
    if missing and scenario_votes:
        winner = max(scenario_votes, key=scenario_votes.get)
        scenario_votes[winner] += missing
    most_common = {
        days: round(count / max(1, scenario_count), 4)
        for days, count in sorted(scenario_votes.items(), key=lambda item: (-item[1], item[0]))
    }
    sensitivity_reasons = []
    if boundary:
        sensitivity_reasons.append("civil_cutoff_sensitive")
    if disagreement:
        sensitivity_reasons.append("physics_precedent_disagreement")
    if committee and str(committee.get("method_regime_risk")) != "low":
        sensitivity_reasons.append(f"committee_rule_entropy_{committee.get('method_regime_risk')}")
    if review_penalty:
        sensitivity_reasons.append("manual_review_recommended")
    risk_label = "GREEN" if flip_rate < 0.01 else "YELLOW" if flip_rate <= 0.15 else "RED"
    return {
        "flip_rate": round(flip_rate, 4),
        "stable": flip_rate < 0.01 and top >= 0.95,
        "tested_scenarios": scenario_count,
        "most_common_values": most_common,
        "sensitivity_reasons": sensitivity_reasons,
        "risk_label": risk_label,
        "probability_margin": round(max(0.0, top - second), 4),
        "method": "deterministic_cutoff_rule_posterior_precedent_sensitivity_v2",
    }
