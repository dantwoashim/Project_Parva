"""Loan and interest impact simulation for calendar mismatches."""

from __future__ import annotations

from typing import Any

from .compare import external_year_map
from .day_count_conventions import SUPPORTED_DAY_COUNT_METHODS, interest_difference
from .models import METHOD_VERSION
from .schedule_simulator import add_bs_month


def simulate_loan_impact(payload: dict[str, Any], *, predict_fn) -> dict[str, Any]:
    try:
        start_year_text, start_month_text, _ = str(payload["loan_start_bs"]).split("-")
        start_year = int(start_year_text)
        start_month = int(start_month_text)
        term_months = int(payload["term_months"])
        principal = float(payload["principal"])
        annual_rate = float(payload["annual_rate"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(
            "loan_start_bs, term_months, principal, and annual_rate are required."
        ) from exc

    if start_month < 1 or start_month > 12:
        raise ValueError("loan_start_bs month must be between 1 and 12.")
    if term_months <= 0 or term_months > 600:
        raise ValueError("term_months must be between 1 and 600.")
    if principal < 0 or annual_rate < 0:
        raise ValueError("principal and annual_rate must be non-negative.")
    day_count_method = payload.get("day_count_method", "actual_365")
    if day_count_method not in SUPPORTED_DAY_COUNT_METHODS:
        raise ValueError(
            "day_count_method must be one of: " + ", ".join(sorted(SUPPORTED_DAY_COUNT_METHODS))
        )

    external_years = payload.get("external_years") or []
    external = external_year_map(external_years) if external_years else {}
    impacted_periods: list[dict[str, Any]] = []
    compared_periods = 0
    for installment in range(1, term_months + 1):
        year, month = add_bs_month(start_year, start_month, installment - 1)
        parva_days = predict_fn(year)["months"][month - 1]
        external_days = external.get(year, [None] * 12)[month - 1]
        if external_days is None:
            continue
        compared_periods += 1
        if external_days == parva_days:
            continue
        day_difference = parva_days - external_days
        interest_delta = interest_difference(
            principal=principal,
            annual_rate=annual_rate,
            day_difference=day_difference,
            day_count_method=day_count_method,
        )
        impacted_periods.append(
            {
                "installment": installment,
                "bs_month": f"{year}-{month:02d}",
                "external_month_days": external_days,
                "parva_month_days": parva_days,
                "day_difference": day_difference,
                "interest_difference_npr": round(interest_delta, 2),
            }
        )

    total_interest_difference = round(sum(row["interest_difference_npr"] for row in impacted_periods), 2)
    max_shift = max((abs(row["day_difference"]) for row in impacted_periods), default=0)
    risk_level = "low"
    if impacted_periods and (abs(total_interest_difference) >= 1000 or max_shift >= 2):
        risk_level = "high"
    elif impacted_periods:
        risk_level = "medium"

    return {
        "summary": {
            "periods_compared": compared_periods,
            "calendar_mismatches_affecting_schedule": len(impacted_periods),
            "calendar_accuracy": round(
                ((compared_periods - len(impacted_periods)) / compared_periods) * 100,
                2,
            )
            if compared_periods
            else None,
            "contract_weighted_accuracy": round(
                100
                - min(
                    100.0,
                    (abs(total_interest_difference) / principal) * 100 if principal else 0.0,
                ),
                4,
            )
            if compared_periods
            else None,
            "interest_impact_weighted_risk": risk_level,
            "first_impacted_installment": impacted_periods[0]["installment"] if impacted_periods else None,
            "max_due_date_shift_days": max_shift,
            "estimated_interest_difference_npr": total_interest_difference,
            "risk_level": risk_level,
        },
        "impacted_periods": impacted_periods,
        "assumptions": {
            "day_count_method": day_count_method,
            "interest_formula": "principal * annual_rate * day_difference / 365",
            "calendar_a": payload.get("calendar_a", "external_sheet"),
            "calendar_b": payload.get("calendar_b", "parva_prediction"),
        },
        "method_version": METHOD_VERSION,
    }
