"""Nepal fiscal-period helpers derived from official BS dates."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.calendar.bikram_sambat import gregorian_to_bs, is_valid_bs_date

FISCAL_YEAR_START_BS_MONTH = 4  # Shrawan


@dataclass(frozen=True)
class BSFiscalPeriod:
    """Fiscal-period metadata for a valid Bikram Sambat date."""

    bs_year: int
    bs_month: int
    bs_day: int
    fiscal_year_start: int
    fiscal_year_end: int
    fiscal_year_label: str
    fiscal_month: int
    fiscal_quarter: int


def fiscal_month_for_bs_month(bs_month: int) -> int:
    """Return Nepal fiscal month number for a BS month.

    Shrawan is fiscal month 1. Ashadh is fiscal month 12.
    """
    if bs_month < 1 or bs_month > 12:
        raise ValueError(f"Invalid BS month: {bs_month}. Must be 1-12.")
    return ((bs_month - FISCAL_YEAR_START_BS_MONTH) % 12) + 1


def fiscal_year_start_for_bs_date(bs_year: int, bs_month: int) -> int:
    """Return the BS year in which the fiscal year starts."""
    if bs_month < 1 or bs_month > 12:
        raise ValueError(f"Invalid BS month: {bs_month}. Must be 1-12.")
    return bs_year if bs_month >= FISCAL_YEAR_START_BS_MONTH else bs_year - 1


def fiscal_year_label(fiscal_year_start: int) -> str:
    """Return a compact Nepal fiscal-year label such as ``2080/81``."""
    return f"{fiscal_year_start}/{(fiscal_year_start + 1) % 100:02d}"


def fiscal_period_for_bs_date(bs_year: int, bs_month: int, bs_day: int) -> BSFiscalPeriod:
    """Return fiscal metadata for a valid BS date."""
    if not is_valid_bs_date(bs_year, bs_month, bs_day):
        raise ValueError(f"Invalid BS date: {bs_year:04d}-{bs_month:02d}-{bs_day:02d}")

    year_start = fiscal_year_start_for_bs_date(bs_year, bs_month)
    fiscal_month = fiscal_month_for_bs_month(bs_month)
    return BSFiscalPeriod(
        bs_year=bs_year,
        bs_month=bs_month,
        bs_day=bs_day,
        fiscal_year_start=year_start,
        fiscal_year_end=year_start + 1,
        fiscal_year_label=fiscal_year_label(year_start),
        fiscal_month=fiscal_month,
        fiscal_quarter=((fiscal_month - 1) // 3) + 1,
    )


def fiscal_period_for_gregorian(gregorian_date: date) -> BSFiscalPeriod:
    """Convert an AD date to BS and return Nepal fiscal metadata."""
    bs_year, bs_month, bs_day = gregorian_to_bs(gregorian_date)
    return fiscal_period_for_bs_date(bs_year, bs_month, bs_day)
