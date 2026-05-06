"""BS month schedule helpers."""

from __future__ import annotations


def add_bs_month(year: int, month: int, offset_months: int) -> tuple[int, int]:
    month_zero = (year * 12 + (month - 1)) + offset_months
    next_year, next_month_zero = divmod(month_zero, 12)
    return next_year, next_month_zero + 1
