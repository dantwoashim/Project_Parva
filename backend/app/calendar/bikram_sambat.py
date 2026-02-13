"""
Bikram Sambat Calendar Conversion
=================================

This module provides accurate conversion between Bikram Sambat (BS)
and Gregorian calendars.

The Bikram Sambat calendar is Nepal's official calendar. It is approximately
56 years, 8 months, and 14 days ahead of the Gregorian calendar, but month
lengths vary by year in a non-formulaic way.

Supported Range (official lookup): 2070-2095 BS (2013-2038 AD)
Extended Range (estimated, sankranti-based): ±200 BS years around lookup

Usage:
    >>> from app.calendar.bikram_sambat import bs_to_gregorian, gregorian_to_bs
    
    >>> bs_to_gregorian(2080, 1, 1)
    datetime.date(2023, 4, 14)
    
    >>> gregorian_to_bs(date(2026, 4, 14))
    (2083, 1, 1)
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import NamedTuple, Tuple, Optional, Dict, Any
from pathlib import Path
import json

from .constants import (
    BS_CALENDAR_DATA,
    BS_MIN_YEAR,
    BS_MAX_YEAR,
    BS_MONTH_NAMES,
    BS_MONTH_NAMES_NEPALI,
    get_bs_year_data,
)
from .sankranti import get_sankrantis_in_year, find_mesh_sankranti
from .ephemeris.swiss_eph import calculate_sunrise
from .ephemeris.time_utils import to_nepal_time


class BSDate(NamedTuple):
    """
    Represents a date in the Bikram Sambat calendar.
    
    Attributes:
        year: BS year (e.g., 2080)
        month: Month number 1-12 (1=Baishakh, 12=Chaitra)
        day: Day of month (1-32)
    """
    year: int
    month: int
    day: int
    
    def __str__(self) -> str:
        """Format as YYYY-MM-DD BS."""
        return f"{self.year}-{self.month:02d}-{self.day:02d}"
    
    @property
    def month_name(self) -> str:
        """Get English month name."""
        return get_bs_month_name(self.month)
    
    @property
    def month_name_nepali(self) -> str:
        """Get Nepali month name."""
        return get_bs_month_name_nepali(self.month)


def is_valid_bs_date(year: int, month: int, day: int) -> bool:
    """
    Check if a BS date is valid.
    
    Args:
        year: BS year
        month: Month number (1-12)
        day: Day of month
    
    Returns:
        True if the date is valid, False otherwise
    
    Examples:
        >>> is_valid_bs_date(2080, 1, 15)
        True
        >>> is_valid_bs_date(2080, 13, 1)  # Invalid month
        False
        >>> is_valid_bs_date(2080, 1, 35)  # Day too high
        False
        >>> is_valid_bs_date(2050, 1, 1)   # Year out of range
        False
    """
    # Check year range
    if year < BS_MIN_YEAR or year > BS_MAX_YEAR:
        return False
    
    # Check month range
    if month < 1 or month > 12:
        return False
    
    # Check day range
    if day < 1:
        return False
    
    # Get days in this month
    max_day = days_in_bs_month(year, month)
    return day <= max_day


def days_in_bs_month(year: int, month: int) -> int:
    """
    Get the number of days in a specific BS month.
    
    Args:
        year: BS year
        month: Month number (1-12, where 1=Baishakh)
    
    Returns:
        Number of days in that month (29-32)
    
    Raises:
        ValueError: If year is out of supported range or month is invalid
    
    Examples:
        >>> days_in_bs_month(2080, 1)  # Baishakh 2080
        31
        >>> days_in_bs_month(2080, 8)  # Mangsir 2080
        29
    """
    if month < 1 or month > 12:
        raise ValueError(f"Invalid month: {month}. Must be 1-12.")
    
    data = get_bs_year_data(year)
    if data is None:
        raise ValueError(
            f"BS year {year} is not in supported range ({BS_MIN_YEAR}-{BS_MAX_YEAR})"
        )
    
    month_lengths, _ = data
    return month_lengths[month - 1]


def get_bs_month_name(month: int) -> str:
    """
    Get the English name of a BS month.
    
    Args:
        month: Month number (1-12)
    
    Returns:
        Month name in English (e.g., "Baishakh")
    
    Raises:
        ValueError: If month is not 1-12
    
    Examples:
        >>> get_bs_month_name(1)
        'Baishakh'
        >>> get_bs_month_name(6)
        'Ashwin'
    """
    if month < 1 or month > 12:
        raise ValueError(f"Invalid month: {month}. Must be 1-12.")
    return BS_MONTH_NAMES[month - 1]


def get_bs_month_name_nepali(month: int) -> str:
    """
    Get the Nepali name of a BS month.
    
    Args:
        month: Month number (1-12)
    
    Returns:
        Month name in Nepali (e.g., "बैशाख")
    
    Raises:
        ValueError: If month is not 1-12
    
    Examples:
        >>> get_bs_month_name_nepali(1)
        'बैशाख'
        >>> get_bs_month_name_nepali(6)
        'आश्विन'
    """
    if month < 1 or month > 12:
        raise ValueError(f"Invalid month: {month}. Must be 1-12.")
    return BS_MONTH_NAMES_NEPALI[month - 1]


def bs_to_gregorian(year: int, month: int, day: int) -> date:
    """
    Convert a Bikram Sambat date to Gregorian.
    
    Uses official lookup table for supported range. If out of range,
    falls back to sankranti-based estimated conversion.
    
    Args:
        year: BS year (e.g., 2080)
        month: Month number (1-12, where 1=Baishakh)
        day: Day of month (1-32)
    
    Returns:
        Corresponding Gregorian date
    
    Raises:
        ValueError: If the BS date is invalid or out of supported range
    
    Examples:
        >>> bs_to_gregorian(2080, 1, 1)  # BS New Year 2080
        datetime.date(2023, 4, 14)
        
        >>> bs_to_gregorian(2083, 1, 1)  # BS New Year 2083
        datetime.date(2026, 4, 14)
        
        >>> bs_to_gregorian(2080, 12, 30)  # Last day of 2080
        datetime.date(2024, 4, 12)
    """
    # Check explicit overrides first
    override = _get_gregorian_override_for_bs(year, month, day)
    if override is not None:
        return override

    # If in official lookup range, use exact table
    if BS_MIN_YEAR <= year <= BS_MAX_YEAR:
        if not is_valid_bs_date(year, month, day):
            raise ValueError(
                f"Invalid BS date: {year}-{month:02d}-{day:02d}. "
                f"Year must be {BS_MIN_YEAR}-{BS_MAX_YEAR}, month 1-12, "
                f"and day must be valid for that month."
            )
        
        data = get_bs_year_data(year)
        if data is None:
            raise ValueError(f"BS year {year} not in lookup table")
        
        month_lengths, year_start = data
        days_from_year_start = day - 1
        for m in range(month - 1):
            days_from_year_start += month_lengths[m]
        return year_start + timedelta(days=days_from_year_start)
    
    return _bs_to_gregorian_estimated(year, month, day)


def bs_to_gregorian_estimated(year: int, month: int, day: int) -> date:
    """
    Convert BS to Gregorian using the estimated (sankranti-based) mode only.

    Useful for explicit overlap analysis and diagnostics.
    """
    return _bs_to_gregorian_estimated(year, month, day)


def _gregorian_to_bs_official(gregorian_date: date) -> tuple[int, int, int]:
    """
    Convert a Gregorian date to Bikram Sambat.
    
    Args:
        gregorian_date: A Python date object
    
    Returns:
        Tuple of (year, month, day) in BS calendar
    
    Raises:
        ValueError: If the date is outside the extended range
    
    Examples:
        >>> gregorian_to_bs(date(2023, 4, 14))  # BS New Year 2080
        (2080, 1, 1)
        
        >>> gregorian_to_bs(date(2026, 4, 14))  # BS New Year 2083
        (2083, 1, 1)
        
        >>> gregorian_to_bs(date(2023, 12, 25))  # Christmas 2023
        (2080, 9, 10)
    """
    # Find which BS year this falls in (official lookup)
    bs_year = None
    year_start = None
    
    for year, (month_lengths, start_date) in sorted(BS_CALENDAR_DATA.items()):
        # Calculate end of this BS year (exclusive - first day of next year)
        year_end_exclusive = start_date + timedelta(days=sum(month_lengths))
        
        # Use exclusive comparison for end to avoid overlap with next year
        if start_date <= gregorian_date < year_end_exclusive:
            bs_year = year
            year_start = start_date
            break
    
    if bs_year is None:
        # Check if it's before our range
        min_start = BS_CALENDAR_DATA[BS_MIN_YEAR][1]
        max_data = BS_CALENDAR_DATA[BS_MAX_YEAR]
        max_end = max_data[1] + timedelta(days=sum(max_data[0]) - 1)
        
        raise ValueError(
            f"Date {gregorian_date} is outside supported range "
            f"({min_start} to {max_end})"
        )
    
    # Calculate days from start of BS year
    days_from_year_start = (gregorian_date - year_start).days
    
    # Find month and day
    month_lengths = BS_CALENDAR_DATA[bs_year][0]
    remaining_days = days_from_year_start
    
    for month_idx, month_len in enumerate(month_lengths):
        if remaining_days < month_len:
            # Found the month
            return (bs_year, month_idx + 1, remaining_days + 1)
        remaining_days -= month_len
    
    # Should not reach here if data is correct
    raise ValueError(f"Failed to convert {gregorian_date} - data inconsistency")


def gregorian_to_bs(gregorian_date: date) -> tuple[int, int, int]:
    """
    Convert a Gregorian date to Bikram Sambat.
    
    Uses official lookup table for supported range. If out of range,
    falls back to sankranti-based estimated conversion.
    """
    # Check explicit overrides first
    override = _get_bs_override_for_gregorian(gregorian_date)
    if override is not None:
        return override
    try:
        return _gregorian_to_bs_official(gregorian_date)
    except ValueError:
        return _gregorian_to_bs_estimated(gregorian_date)


def gregorian_to_bs_official(gregorian_date: date) -> tuple[int, int, int]:
    """
    Convert a Gregorian date to BS using official lookup only.
    
    Raises:
        ValueError if date is outside the official range.
    """
    # Check explicit overrides first
    override = _get_bs_override_for_gregorian(gregorian_date)
    if override is not None:
        return override
    return _gregorian_to_bs_official(gregorian_date)


def gregorian_to_bs_estimated(gregorian_date: date) -> tuple[int, int, int]:
    """
    Convert a Gregorian date to BS using sankranti-based estimation.
    
    Raises:
        ValueError if date is outside the extended estimated range.
    """
    # Overrides should always win, even in estimated mode
    override = _get_bs_override_for_gregorian(gregorian_date)
    if override is not None:
        return override
    return _gregorian_to_bs_estimated(gregorian_date)


def estimated_bs_to_gregorian(year: int, month: int, day: int) -> date:
    """
    Explicit alias for estimated BS->Gregorian conversion.
    """
    return bs_to_gregorian_estimated(year, month, day)


def estimated_gregorian_to_bs(gregorian_date: date) -> tuple[int, int, int]:
    """
    Explicit alias for estimated Gregorian->BS conversion.
    """
    return gregorian_to_bs_estimated(gregorian_date)


def _estimated_bs_year_range() -> tuple[int, int]:
    """
    Return supported estimated range around official lookup.
    """
    past = 200
    future = 200
    return (BS_MIN_YEAR - past, BS_MAX_YEAR + future)


def _bs_to_gregorian_estimated(year: int, month: int, day: int) -> date:
    """
    Internal estimated BS->Gregorian conversion using sankranti boundaries.
    """
    min_year, max_year = _estimated_bs_year_range()
    if year < min_year or year > max_year:
        raise ValueError(
            f"BS year {year} is outside estimated range ({min_year}-{max_year})"
        )
    if month < 1 or month > 12:
        raise ValueError(f"Invalid month: {month}. Must be 1-12.")
    if day < 1 or day > 32:
        raise ValueError(f"Invalid day: {day}. Must be 1-32.")

    month_starts = _get_bs_month_starts_estimated(year)
    start_date = None
    next_start = None
    for idx, (m_num, d_start) in enumerate(month_starts):
        if m_num == month:
            start_date = d_start
            next_start = (
                month_starts[idx + 1][1]
                if idx + 1 < len(month_starts)
                else _get_mesh_sankranti_date(year - 57 + 1)
            )
            break

    if start_date is None:
        raise ValueError(f"Could not determine month start for {year}-{month:02d}")

    month_length = (next_start - start_date).days
    if day > month_length:
        raise ValueError(
            f"Invalid day {day} for estimated BS month {year}-{month:02d} "
            f"(max {month_length})"
        )

    return start_date + timedelta(days=day - 1)


# =============================================================================
# BS OVERRIDES (manual corrections)
# =============================================================================

_bs_overrides_cache: Optional[Dict[str, Any]] = None


def _load_bs_overrides() -> Dict[str, Any]:
    global _bs_overrides_cache
    if _bs_overrides_cache is not None:
        return _bs_overrides_cache
    path = Path(__file__).parent / "bs_overrides.json"
    if not path.exists():
        _bs_overrides_cache = {"gregorian_to_bs": {}, "bs_to_gregorian": {}}
        return _bs_overrides_cache
    with open(path, "r", encoding="utf-8") as f:
        _bs_overrides_cache = json.load(f)
    # Ensure keys exist
    _bs_overrides_cache.setdefault("gregorian_to_bs", {})
    _bs_overrides_cache.setdefault("bs_to_gregorian", {})
    return _bs_overrides_cache


def _get_bs_override_for_gregorian(gregorian_date: date) -> Optional[Tuple[int, int, int]]:
    data = _load_bs_overrides()
    entry = data.get("gregorian_to_bs", {}).get(gregorian_date.isoformat())
    if not entry:
        return None
    return (int(entry["year"]), int(entry["month"]), int(entry["day"]))


def _get_gregorian_override_for_bs(year: int, month: int, day: int) -> Optional[date]:
    data = _load_bs_overrides()
    key = f"{year:04d}-{month:02d}-{day:02d}"
    entry = data.get("bs_to_gregorian", {}).get(key)
    if not entry:
        return None
    return date.fromisoformat(entry)


def _sankranti_start_date(sankranti_utc: datetime) -> date:
    """
    Determine the BS month start date for a sankranti moment.
    
    Rule (Nepal convention):
    - If sankranti occurs before sunrise, month starts that day.
    - If sankranti occurs after sunrise, month starts next day.
    """
    local = to_nepal_time(sankranti_utc)
    local_date = local.date()
    sunrise_utc = calculate_sunrise(local_date)
    sunrise_local = to_nepal_time(sunrise_utc)
    if local <= sunrise_local:
        return local_date
    return local_date + timedelta(days=1)


def _get_mesh_sankranti_date(gregorian_year: int) -> date:
    """
    Get Mesh Sankranti date in Nepal time for a Gregorian year.
    """
    dt = find_mesh_sankranti(gregorian_year)
    if dt is None:
        raise ValueError(f"Mesh Sankranti not found for {gregorian_year}")
    return _sankranti_start_date(dt)


def _get_bs_month_starts_estimated(bs_year: int) -> list[tuple[int, date]]:
    """
    Build month start dates for a BS year using sankranti transitions.
    
    Returns:
        List of (bs_month_number, start_date) tuples, sorted by start_date.
    """
    min_year, max_year = _estimated_bs_year_range()
    if bs_year < min_year or bs_year > max_year:
        raise ValueError(
            f"BS year {bs_year} is outside estimated range ({min_year}-{max_year})"
        )
    
    greg_year = bs_year - 57  # Mesh Sankranti for this BS year
    mesh_start = _get_mesh_sankranti_date(greg_year)
    mesh_next = _get_mesh_sankranti_date(greg_year + 1)
    
    sankrantis = get_sankrantis_in_year(greg_year) + get_sankrantis_in_year(greg_year + 1)
    month_starts = []
    for s in sankrantis:
        d = _sankranti_start_date(s["datetime_utc"])
        if mesh_start <= d < mesh_next:
            month_starts.append((s["bs_month_number"], d))
    
    month_starts.sort(key=lambda x: x[1])
    
    if len(month_starts) != 12:
        raise ValueError(
            f"Expected 12 sankranti starts for BS year {bs_year}, got {len(month_starts)}"
        )
    
    return month_starts


def _gregorian_to_bs_estimated(gregorian_date: date) -> tuple[int, int, int]:
    """
    Estimate BS conversion using sankranti boundaries (200-year window).
    """
    # Determine BS year based on Mesh Sankranti date
    mesh_this = _get_mesh_sankranti_date(gregorian_date.year)
    if gregorian_date >= mesh_this:
        bs_year = gregorian_date.year + 57
        start_mesh_year = gregorian_date.year
        mesh_start = mesh_this
    else:
        bs_year = gregorian_date.year + 56
        start_mesh_year = gregorian_date.year - 1
        mesh_start = _get_mesh_sankranti_date(start_mesh_year)
    
    min_year, max_year = _estimated_bs_year_range()
    if bs_year < min_year or bs_year > max_year:
        raise ValueError(
            f"Date {gregorian_date} maps to BS year {bs_year}, "
            f"outside estimated range ({min_year}-{max_year})"
        )
    
    mesh_next = _get_mesh_sankranti_date(start_mesh_year + 1)
    
    # Build month starts for this BS year
    sankrantis = get_sankrantis_in_year(start_mesh_year) + get_sankrantis_in_year(start_mesh_year + 1)
    month_starts = []
    for s in sankrantis:
        d = _sankranti_start_date(s["datetime_utc"])
        if mesh_start <= d < mesh_next:
            month_starts.append((s["bs_month_number"], d))
    month_starts.sort(key=lambda x: x[1])
    
    if len(month_starts) != 12:
        raise ValueError(
            f"Expected 12 sankranti starts for BS year {bs_year}, got {len(month_starts)}"
        )
    
    # Determine BS month and day
    for idx, (month_num, start_date) in enumerate(month_starts):
        next_start = month_starts[idx + 1][1] if idx + 1 < len(month_starts) else mesh_next
        if start_date <= gregorian_date < next_start:
            day = (gregorian_date - start_date).days + 1
            return (bs_year, month_num, day)
    
    raise ValueError(f"Failed to estimate BS date for {gregorian_date}")


def get_bs_confidence(gregorian_date: date) -> str:
    """
    Return confidence level for BS conversion of a Gregorian date.
    
    Returns:
        "official" when the date is within the lookup table range,
        otherwise "estimated".
    """
    # Overrides are treated as official corrections
    if _get_bs_override_for_gregorian(gregorian_date) is not None:
        return "official"

    min_start = BS_CALENDAR_DATA[BS_MIN_YEAR][1]
    max_data = BS_CALENDAR_DATA[BS_MAX_YEAR]
    max_end = max_data[1] + timedelta(days=sum(max_data[0]) - 1)
    
    if min_start <= gregorian_date <= max_end:
        return "official"
    return "estimated"


def get_bs_year_confidence(bs_year: int) -> str:
    """
    Return confidence level for a BS year.
    
    Returns:
        "official" when the BS year is within lookup range,
        otherwise "estimated".
    """
    if BS_MIN_YEAR <= bs_year <= BS_MAX_YEAR:
        return "official"
    return "estimated"


def get_bs_source_range(gregorian_date: date) -> str | None:
    """
    Return official source range label when lookup-backed, else None.
    """
    confidence = get_bs_confidence(gregorian_date)
    if confidence == "official":
        return f"{BS_MIN_YEAR}-{BS_MAX_YEAR}"
    return None


def get_bs_estimated_error_days(gregorian_date: date) -> str | None:
    """
    Return documented error bound for estimated conversion mode.
    """
    if get_bs_confidence(gregorian_date) == "estimated":
        return "0-1"
    return None


def gregorian_to_bs_date(gregorian_date: date) -> BSDate:
    """
    Convert a Gregorian date to a BSDate object.
    
    This is a convenience function that returns a BSDate NamedTuple
    instead of a raw tuple.
    
    Args:
        gregorian_date: A Python date object
    
    Returns:
        BSDate object with year, month, day attributes
    
    Examples:
        >>> bs = gregorian_to_bs_date(date(2023, 4, 14))
        >>> bs.year
        2080
        >>> bs.month_name
        'Baishakh'
    """
    year, month, day = gregorian_to_bs(gregorian_date)
    return BSDate(year, month, day)


def get_bs_year_start(year: int) -> date:
    """
    Get the Gregorian date when a BS year starts.
    
    Args:
        year: BS year
    
    Returns:
        Gregorian date of Baishakh 1 of that year
    
    Raises:
        ValueError: If year is out of supported range
    
    Examples:
        >>> get_bs_year_start(2080)
        datetime.date(2023, 4, 14)
        >>> get_bs_year_start(2083)
        datetime.date(2026, 4, 14)
    """
    data = get_bs_year_data(year)
    if data is None:
        raise ValueError(
            f"BS year {year} is not in supported range ({BS_MIN_YEAR}-{BS_MAX_YEAR})"
        )
    return data[1]


def get_bs_year_end(year: int) -> date:
    """
    Get the Gregorian date when a BS year ends.
    
    Args:
        year: BS year
    
    Returns:
        Gregorian date of Chaitra last day of that year
    
    Raises:
        ValueError: If year is out of supported range
    
    Examples:
        >>> get_bs_year_end(2080)
        datetime.date(2024, 4, 12)
    """
    data = get_bs_year_data(year)
    if data is None:
        raise ValueError(
            f"BS year {year} is not in supported range ({BS_MIN_YEAR}-{BS_MAX_YEAR})"
        )
    month_lengths, start_date = data
    total_days = sum(month_lengths)
    return start_date + timedelta(days=total_days - 1)


def format_bs_date(year: int, month: int, day: int, style: str = "long") -> str:
    """
    Format a BS date as a human-readable string.
    
    Args:
        year: BS year
        month: Month number
        day: Day of month
        style: One of "long", "short", "nepali"
    
    Returns:
        Formatted date string
    
    Examples:
        >>> format_bs_date(2080, 6, 15, "long")
        '15 Ashwin, 2080'
        >>> format_bs_date(2080, 6, 15, "short")
        '2080-06-15'
        >>> format_bs_date(2080, 6, 15, "nepali")
        '१५ आश्विन, २०८०'
    """
    if style == "short":
        return f"{year}-{month:02d}-{day:02d}"
    elif style == "nepali":
        # Convert numbers to Nepali digits
        nepali_digits = "०१२३४५६७८९"
        def to_nepali(n: int) -> str:
            return "".join(nepali_digits[int(d)] for d in str(n))
        return f"{to_nepali(day)} {get_bs_month_name_nepali(month)}, {to_nepali(year)}"
    else:  # long
        return f"{day} {get_bs_month_name(month)}, {year}"


def days_until_bs_date(target_year: int, target_month: int, target_day: int) -> int:
    """
    Calculate days from today until a BS date.
    
    Args:
        target_year: Target BS year
        target_month: Target BS month
        target_day: Target BS day
    
    Returns:
        Number of days until the target date (negative if in past)
    
    Examples:
        >>> days_until_bs_date(2083, 6, 12)  # Days until Indra Jatra 2026
        ... # Returns days remaining
    """
    target_gregorian = bs_to_gregorian(target_year, target_month, target_day)
    today = date.today()
    return (target_gregorian - today).days
