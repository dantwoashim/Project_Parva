"""
Parva Calendar Engine
=====================

Multi-calendar calculation system supporting:
- Bikram Sambat (BS) - Nepal's official calendar
- Nepal Sambat (NS) - Newari lunar calendar  
- Tithi calculations for lunar-based festivals

This module provides accurate date conversions and festival
date calculations for 50+ Nepali festivals.
"""

from .bikram_sambat import (
    bs_to_gregorian,
    gregorian_to_bs,
    gregorian_to_bs_official,
    gregorian_to_bs_estimated,
    get_bs_month_name,
    get_bs_month_name_nepali,
    days_in_bs_month,
    is_valid_bs_date,
)

from .tithi.tithi_core import (
    calculate_tithi,
    TITHI_NAMES,
    get_tithi_name,
)

from .tithi.tithi_boundaries import (
    find_next_tithi,
)

from .tithi.tithi_udaya import (
    get_udaya_tithi,
    get_tithi_for_date,
)

from .ephemeris.positions import (
    get_paksha,
)

from .nepal_sambat import (
    gregorian_year_to_ns,
    ns_year_to_gregorian,
    get_ns_new_year_date,
    is_ns_new_year,
    get_ns_month_name,
    get_current_ns_year,
    format_ns_date,
)

from .calculator import (
    DateRange,
    CalendarRule,
)
from .calculator_v2 import (
    calculate_festival_v2,
    get_upcoming_festivals_v2,
    get_festivals_on_date_v2,
    get_next_occurrence_v2,
    list_festivals_v2,
)


def calculate_festival_date(festival_id: str, year: int, use_overrides: bool = True) -> DateRange:
    """
    Compatibility wrapper: returns DateRange but uses V2 engine internally.
    """
    result = calculate_festival_v2(festival_id, year, use_overrides=use_overrides)
    if result is None:
        raise ValueError(f"Could not calculate festival: {festival_id} ({year})")
    return DateRange(start=result.start_date, end=result.end_date, year=year)


def get_upcoming_festivals(from_date, days: int = 30):
    """
    Compatibility wrapper: returns (festival_id, DateRange) using V2 engine.
    """
    results = []
    for festival_id, fdate in get_upcoming_festivals_v2(from_date, days=days):
        results.append((festival_id, DateRange(start=fdate.start_date, end=fdate.end_date, year=fdate.year)))
    return results


def get_festivals_on_date(target_date):
    """
    Compatibility wrapper: returns (festival_id, DateRange) using V2 engine.
    """
    results = []
    for festival_id, fdate in get_festivals_on_date_v2(target_date):
        results.append((festival_id, DateRange(start=fdate.start_date, end=fdate.end_date, year=fdate.year)))
    return results


def get_next_occurrence(festival_id: str, after_date=None):
    """
    Compatibility wrapper: returns DateRange using V2 engine.
    """
    fdate = get_next_occurrence_v2(festival_id, after_date=after_date)
    if fdate is None:
        raise ValueError(f"Could not find next occurrence: {festival_id}")
    return DateRange(start=fdate.start_date, end=fdate.end_date, year=fdate.year)


def list_all_festivals():
    """Compatibility wrapper: list all festivals using V2 rules + fallback."""
    return list_festivals_v2()

__all__ = [
    # Bikram Sambat
    "bs_to_gregorian",
    "gregorian_to_bs", 
    "gregorian_to_bs_official",
    "gregorian_to_bs_estimated",
    "get_bs_month_name",
    "get_bs_month_name_nepali",
    "days_in_bs_month",
    "is_valid_bs_date",
    # Tithi (v2.0 ephemeris-based)
    "calculate_tithi",
    "get_paksha",
    "find_next_tithi",
    "get_tithi_name",
    "get_udaya_tithi",
    "get_tithi_for_date",
    "TITHI_NAMES",
    # Nepal Sambat
    "gregorian_year_to_ns",
    "ns_year_to_gregorian",
    "get_ns_new_year_date",
    "is_ns_new_year",
    "get_ns_month_name",
    "get_current_ns_year",
    "format_ns_date",
    # Calculator
    "calculate_festival_date",
    "get_upcoming_festivals",
    "get_festivals_on_date",
    "get_next_occurrence",
    "list_all_festivals",
    "DateRange",
    "CalendarRule",
]
