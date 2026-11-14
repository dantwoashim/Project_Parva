"""Fiscal date boundaries; no tax or payroll eligibility decisions."""

from datetime import date

from . import bs


def fiscal_year(day: date) -> tuple[int, date, date]:
    """Return the starting BS year and inclusive AD bounds (Shrawan-Ashadh)."""
    value = bs.to_bs(day)
    year = value.year if value.month >= 4 else value.year - 1
    return year, bs.to_ad(year, 4, 1), bs.to_ad(year + 1, 3, bs.month_days(year + 1, 3))
