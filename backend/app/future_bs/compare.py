"""External month-length sheet comparison helpers."""

from __future__ import annotations

from typing import Any

from app.calendar.constants import BS_MONTH_NAMES

from .models import METHOD_VERSION, MONTH_DAY_VALUES


def _comparison_category(their_days: int, parva_days: int, detail: dict[str, Any]) -> str:
    risk_flags = set(detail.get("risk_flags") or [])
    confidence_score = float(detail.get("confidence_score", 0.0))
    high_confidence = confidence_score >= 0.95 and "manual_review_recommended" not in risk_flags
    low_confidence = confidence_score < 0.85 or "manual_review_recommended" in risk_flags
    if their_days == parva_days:
        return "AGREE_HIGH_CONFIDENCE" if high_confidence else "AGREE_LOW_CONFIDENCE"
    if high_confidence:
        return "PARVA_HIGH_CONFIDENCE_DISAGREES"
    if low_confidence:
        return "BOTH_UNCERTAIN"
    return "NEEDS_OFFICIAL_REVIEW"


def external_year_map(years: list[dict[str, Any]]) -> dict[int, list[int]]:
    mapped: dict[int, list[int]] = {}
    for row in years:
        try:
            bs_year = int(row["bs_year"])
            months = [int(value) for value in row["months"]]
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Each external year must include bs_year and 12 numeric months.") from exc
        if len(months) != 12:
            raise ValueError(f"External year {bs_year} must contain exactly 12 month lengths.")
        if any(days not in MONTH_DAY_VALUES for days in months):
            raise ValueError(f"External year {bs_year} contains a month length outside 29-32 days.")
        mapped[bs_year] = months
    return mapped


def compare_external_sheet(
    source_name: str,
    years: list[dict[str, Any]],
    *,
    predict_fn,
) -> dict[str, Any]:
    external = external_year_map(years)
    mismatches: list[dict[str, Any]] = []
    category_counts: dict[str, int] = {}
    matches = 0
    months_compared = 0

    for bs_year, external_months in sorted(external.items()):
        prediction = predict_fn(bs_year)
        for index, (their_days, parva_days) in enumerate(
            zip(external_months, prediction["months"]),
            start=1,
        ):
            months_compared += 1
            month_detail = prediction["month_details"][index - 1]
            category = _comparison_category(their_days, parva_days, month_detail)
            category_counts[category] = category_counts.get(category, 0) + 1
            if their_days == parva_days:
                matches += 1
                continue
            mismatches.append(
                {
                    "bs_year": bs_year,
                    "month": index,
                    "month_name": BS_MONTH_NAMES[index - 1],
                    "their_days": their_days,
                    "parva_days": parva_days,
                    "parva_probability": month_detail["probability"],
                    "confidence": month_detail["confidence_label"],
                    "confidence_score": month_detail.get("confidence_score"),
                    "risk_flags": month_detail["risk_flags"],
                    "comparison_category": category,
                    "recommendation": "manual review before loan or contract use",
                }
            )

    return {
        "source_name": source_name,
        "summary": {
            "years_compared": len(external),
            "months_compared": months_compared,
            "matches": matches,
            "mismatches": len(mismatches),
            "match_rate": round((matches / months_compared) * 100, 2) if months_compared else 0.0,
            "category_counts": category_counts,
        },
        "mismatches": mismatches,
        "method_version": METHOD_VERSION,
    }
