"""Year-level month sequence decoder with valid-total constraints."""

from __future__ import annotations

import math
from typing import Any

from .models import MONTH_DAY_VALUES

ALLOWED_YEAR_TOTALS = (365, 366)


def _month_candidate_map(detail: dict[str, Any]) -> dict[int, float]:
    probabilities = detail.get("probability") or {}
    current = int(detail.get("final_days", detail.get("days", 30)))
    values: dict[int, float] = {current: max(0.001, float(detail.get("confidence_score", 0.8) or 0.8))}
    for days in MONTH_DAY_VALUES:
        prob = float(probabilities.get(str(days), probabilities.get(f"{days}_days", 0.0)) or 0.0)
        if prob > 0:
            values[days] = max(values.get(days, 0.0), prob)
    total = sum(values.values()) or 1.0
    return {days: max(prob / total, 0.001) for days, prob in values.items()}


def decode_year_sequence(
    bs_year: int,
    month_details: list[dict[str, Any]],
    *,
    allowed_year_totals: tuple[int, ...] = ALLOWED_YEAR_TOTALS,
    min_supported_probability: float = 0.02,
) -> dict[str, Any]:
    candidates = []
    for detail in month_details:
        mapped = {
            days: prob
            for days, prob in _month_candidate_map(detail).items()
            if prob >= min_supported_probability or days == int(detail.get("final_days", days))
        }
        candidates.append(mapped)

    states: dict[int, tuple[float, list[int]]] = {0: (0.0, [])}
    for month_candidates in candidates:
        next_states: dict[int, tuple[float, list[int]]] = {}
        for total, (score, path) in states.items():
            for days, prob in month_candidates.items():
                new_total = total + days
                new_score = score + math.log(max(prob, 0.001))
                if new_total not in next_states or new_score > next_states[new_total][0]:
                    next_states[new_total] = (new_score, [*path, days])
        states = next_states

    original = [int(detail.get("final_days", 30)) for detail in month_details]
    original_total = sum(original)
    valid_options = [(total, value) for total, value in states.items() if total in allowed_year_totals]
    if not valid_options:
        return {
            "bs_year": bs_year,
            "decoded_months": original,
            "decoded_total": original_total,
            "sequence_log_probability": None,
            "adjustments": [],
            "valid": False,
            "claimable": False,
            "reconciliation_explanation": [
                "no_supported_candidate_sequence_reaches_365_or_366_days"
            ],
        }
    decoded_total, (score, decoded) = max(valid_options, key=lambda item: item[1][0])
    adjustments = []
    for index, (before, after) in enumerate(zip(original, decoded), start=1):
        if before != after:
            support = candidates[index - 1].get(after, 0.0)
            adjustments.append(
                {
                    "month": index,
                    "from": before,
                    "to": after,
                    "support_probability": round(support, 6),
                    "support": "model_supported_candidate",
                }
            )
    low_support = any(row["support_probability"] < 0.08 for row in adjustments)
    return {
        "bs_year": bs_year,
        "decoded_months": decoded,
        "decoded_total": decoded_total,
        "sequence_log_probability": round(score, 6),
        "adjustments": adjustments,
        "valid": True,
        "claimable": not low_support,
        "reconciliation_explanation": (
            ["valid_without_adjustment"]
            if not adjustments
            else ["valid_total_selected_by_dynamic_programming"]
        ),
    }
