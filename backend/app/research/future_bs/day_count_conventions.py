"""Day-count convention helpers for loan impact simulation."""

from __future__ import annotations

SUPPORTED_DAY_COUNT_METHODS = {
    "actual_365",
    "actual_360",
    "actual_actual",
    "30_360",
    "monthly_flat",
    "product_specific",
}


def interest_difference(
    *,
    principal: float,
    annual_rate: float,
    day_difference: int,
    day_count_method: str,
) -> float:
    if day_count_method not in SUPPORTED_DAY_COUNT_METHODS:
        raise ValueError(f"Unsupported day_count_method: {day_count_method}")
    rate = annual_rate / 100.0
    if day_count_method == "actual_360":
        divisor = 360.0
    elif day_count_method == "30_360":
        divisor = 360.0
    elif day_count_method == "monthly_flat":
        divisor = 12.0
        return principal * (rate / divisor) * (day_difference / 30.0)
    elif day_count_method == "product_specific":
        divisor = 365.0
    else:
        divisor = 365.0
    return principal * rate * (day_difference / divisor)
