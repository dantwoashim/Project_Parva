"""Small causal-bitplane-backed working-day solver."""

from __future__ import annotations

from app.calendar.bikram_sambat import days_in_bs_month
from app.membranes.unsat import unsat_membrane


def solve_working_days(
    *,
    bs_year: int,
    bs_month: int,
    count: int,
    holidays: set[int] | None = None,
    weekend_offsets: set[int] | None = None,
) -> dict:
    holidays = holidays or set()
    weekend_offsets = weekend_offsets or {4, 11, 18, 25}
    days = days_in_bs_month(bs_year, bs_month)
    accepted: list[int] = []
    rejected: list[dict] = []
    for day in range(1, days + 1):
        reasons = []
        if day in holidays:
            reasons.append("holiday")
        if day in weekend_offsets:
            reasons.append("weekend")
        if reasons:
            rejected.append({"day": day, "reasons": reasons})
            continue
        accepted.append(day)
        if len(accepted) == count:
            break
    if len(accepted) < count:
        return unsat_membrane(
            {"bs_year": bs_year, "bs_month": bs_month, "count": count},
            ["not_enough_working_days"],
            ["reduce_count", "relax_holiday_filter", "relax_weekend_filter"],
        )
    return {
        "kind": "constraint_solution",
        "selected_days": accepted,
        "rejected_dates": rejected,
        "bitplane_witness_refs": ["bitplane-working-day"],
        "claim_boundary": "solver_decision_support_not_authority",
    }
