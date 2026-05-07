"""Explainable year-total reconciliation for future BS predictions."""

from __future__ import annotations

from typing import Any

from .prediction_sets import prediction_set_payload
from .year_total_gate import NORMAL_FUTURE_YEAR_TOTALS, year_total_gate


def reconcile_year_total(payload: dict[str, Any]) -> dict[str, Any]:
    months = [int(value) for value in payload.get("months", [])]
    gate = year_total_gate(months)
    if gate["valid_future_year_total"]:
        return {
            "attempted": False,
            "applied": False,
            "reason": "year_total_already_valid",
            "new_total": gate["year_total_days"],
        }

    target_total = min(NORMAL_FUTURE_YEAR_TOTALS, key=lambda total: abs(total - gate["year_total_days"]))
    delta = target_total - gate["year_total_days"]
    candidates = []
    for index, detail in enumerate(payload.get("month_details") or [], start=1):
        current = int(detail.get("final_days", months[index - 1]))
        sets = prediction_set_payload(detail)
        for option in sets["prediction_set_95"]:
            change = int(option) - current
            if change == 0:
                continue
            probability = sets["probabilities"].get(str(option), 0.0)
            if (delta > 0 and change > 0) or (delta < 0 and change < 0):
                candidates.append(
                    {
                        "month": index,
                        "from": current,
                        "to": int(option),
                        "change": change,
                        "probability": probability,
                        "support": "inside_prediction_set_95",
                    }
                )
    candidates.sort(key=lambda row: (-float(row["probability"]), abs(int(row["change"]))))
    selected = []
    remaining = delta
    for candidate in candidates:
        if remaining == 0:
            break
        change = int(candidate["change"])
        if abs(change) <= abs(remaining) and ((remaining > 0 and change > 0) or (remaining < 0 and change < 0)):
            selected.append(candidate)
            remaining -= change
    if remaining == 0 and selected:
        return {
            "attempted": True,
            "applied": True,
            "adjustments": selected,
            "old_total": gate["year_total_days"],
            "new_total": target_total,
            "reason": "supported_minimal_adjustment",
        }
    return {
        "attempted": True,
        "applied": False,
        "old_total": gate["year_total_days"],
        "target_total": target_total,
        "reason": "no_supported_alternative_reaches_valid_total",
        "candidate_count": len(candidates),
    }
