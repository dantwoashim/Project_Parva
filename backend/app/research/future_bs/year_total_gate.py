"""Strict year-total validation for future BS prediction artifacts."""

from __future__ import annotations

from typing import Any

NORMAL_FUTURE_YEAR_TOTALS = {365, 366}


def year_total_gate(months: list[int]) -> dict[str, Any]:
    total = sum(months)
    valid = total in NORMAL_FUTURE_YEAR_TOTALS
    return {
        "year_total_days": total,
        "allowed_year_totals": sorted(NORMAL_FUTURE_YEAR_TOTALS),
        "valid_future_year_total": valid,
        "risk_label": "GREEN" if valid else "RED",
        "claimable": valid,
        "manual_review_required": not valid,
        "reason": None if valid else "invalid_or_exceptional_year_total",
    }


def apply_year_total_gate(payload: dict[str, Any]) -> dict[str, Any]:
    months = [int(value) for value in payload.get("months", [])]
    gate = year_total_gate(months)
    result = dict(payload)
    result["year_total_gate"] = gate
    constraints = dict(result.get("constraints") or {})
    constraints["normal_future_year_total"] = gate["valid_future_year_total"]
    constraints["claimable_year_total"] = gate["claimable"]
    result["constraints"] = constraints
    if not gate["valid_future_year_total"]:
        flags = set(result.get("risk_flags") or [])
        flags.update({"invalid_or_exceptional_year_total", "manual_review_recommended"})
        result["risk_flags"] = sorted(flags)
        for detail in result.get("month_details") or []:
            month_flags = set(detail.get("risk_flags") or [])
            month_flags.update({"invalid_or_exceptional_year_total", "manual_review_recommended"})
            detail["risk_flags"] = sorted(month_flags)
            detail["confidence_label"] = "computed_red_review_required"
            detail["claimable"] = False
    return result
