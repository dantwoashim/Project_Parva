"""Risk, disagreement, and proof helpers for festival-date surfaces."""

from __future__ import annotations

from datetime import date
from typing import Any


def _alternate_dates(alternate_candidates: list[dict[str, Any]] | None) -> list[date]:
    dates: list[date] = []
    for candidate in alternate_candidates or []:
        value = candidate.get("start")
        if isinstance(value, date):
            dates.append(value)
            continue
        if isinstance(value, str):
            try:
                dates.append(date.fromisoformat(value))
            except ValueError:
                continue
    return dates


def classify_boundary_radar(
    *,
    start_date: date,
    alternate_candidates: list[dict[str, Any]] | None,
    support_tier: str | None,
    fallback_used: bool,
) -> str:
    alternates = _alternate_dates(alternate_candidates)
    if alternates:
        closest_delta = min(abs((alt - start_date).days) for alt in alternates)
        if closest_delta <= 1:
            return "high_disagreement_risk"
        return "one_day_sensitive"

    normalized_tier = str(support_tier or "").strip().lower()
    if fallback_used or normalized_tier in {"heuristic", "estimated", "conflicted"}:
        return "one_day_sensitive"
    return "stable"


def stability_score(
    *,
    start_date: date,
    alternate_candidates: list[dict[str, Any]] | None,
    support_tier: str | None,
    fallback_used: bool,
) -> float:
    normalized_tier = str(support_tier or "").strip().lower()
    base = {
        "authoritative": 0.97,
        "computed": 0.86,
        "conflicted": 0.5,
        "heuristic": 0.58,
        "estimated": 0.45,
    }.get(normalized_tier, 0.62)

    if fallback_used:
        base -= 0.16

    alternates = _alternate_dates(alternate_candidates)
    if alternates:
        base -= 0.22
        closest_delta = min(abs((alt - start_date).days) for alt in alternates)
        if closest_delta <= 1:
            base -= 0.12

    return round(min(max(base, 0.05), 0.99), 2)


def build_risk_payload(
    *,
    start_date: date,
    alternate_candidates: list[dict[str, Any]] | None,
    support_tier: str | None,
    fallback_used: bool,
    risk_mode: str = "standard",
) -> dict[str, Any]:
    boundary_radar = classify_boundary_radar(
        start_date=start_date,
        alternate_candidates=alternate_candidates,
        support_tier=support_tier,
        fallback_used=fallback_used,
    )
    score = stability_score(
        start_date=start_date,
        alternate_candidates=alternate_candidates,
        support_tier=support_tier,
        fallback_used=fallback_used,
    )
    normalized_mode = str(risk_mode or "standard").strip().lower()
    abstained = normalized_mode == "strict" and boundary_radar == "high_disagreement_risk"
    if abstained:
        recommended_action = "Compare authority-backed candidates before relying on a single date."
    elif boundary_radar == "one_day_sensitive":
        recommended_action = "Inspect the explanation and provenance before using this date operationally."
    else:
        recommended_action = "This result is stable enough for normal consumer use."

    return {
        "risk_mode": normalized_mode,
        "boundary_radar": boundary_radar,
        "stability_score": score,
        "abstained": abstained,
        "recommended_action": recommended_action,
    }


def truth_ladder() -> list[dict[str, str]]:
    return [
        {
            "tier": "authoritative",
            "title": "Authoritative",
            "body": "Directly anchored to a published authority-backed date with no active conflict signal.",
        },
        {
            "tier": "computed",
            "title": "Source-supported",
            "body": "Computed through the canonical engine path with stable support and no visible disagreement.",
        },
        {
            "tier": "heuristic",
            "title": "Heuristic",
            "body": "Useful, but softened because defaults, fallbacks, or incomplete support were involved.",
        },
        {
            "tier": "estimated",
            "title": "Estimated",
            "body": "Outside the strongest support zone, so the product is explicit that this is an estimate.",
        },
        {
            "tier": "conflicted",
            "title": "Conflicted",
            "body": "Multiple authority-backed candidates exist, so the public default is shown alongside alternates.",
        },
        {
            "tier": "abstained",
            "title": "Abstained",
            "body": "Strict risk mode chose not to pretend a single date is safe enough to promote as canonical.",
        },
    ]


__all__ = [
    "build_risk_payload",
    "classify_boundary_radar",
    "stability_score",
    "truth_ladder",
]
