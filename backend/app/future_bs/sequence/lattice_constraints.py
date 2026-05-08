"""Lattice constraints for reconstructed month starts."""

from __future__ import annotations

from datetime import date

ALLOWED_YEAR_TOTALS = {365, 366}
PLAUSIBLE_MONTH_LENGTHS = {29, 30, 31, 32}


def valid_month_interval(start_ad: str, next_start_ad: str) -> bool:
    length = (date.fromisoformat(next_start_ad) - date.fromisoformat(start_ad)).days
    return length in PLAUSIBLE_MONTH_LENGTHS


def valid_year_total(total: int) -> bool:
    return int(total) in ALLOWED_YEAR_TOTALS
