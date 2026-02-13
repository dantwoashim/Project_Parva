"""
Festival Date Calculator
========================

This module provides the unified API for calculating festival dates
across multiple calendar systems.

It combines:
- Bikram Sambat conversion (for BS-based festivals)
- Tithi calculations (for lunar-based festivals)
- Calendar rules (for computing any festival date)

Usage:
    >>> from app.calendar.calculator import calculate_festival_date, get_upcoming_festivals
    
    >>> dashain_2026 = calculate_festival_date("dashain", 2026)
    >>> print(dashain_2026)
    
    >>> upcoming = get_upcoming_festivals(date(2026, 9, 1), days=30)
"""

from __future__ import annotations

from datetime import date, timedelta, timezone
from typing import Literal, NamedTuple, Optional, List, Tuple, Dict
from pydantic import BaseModel, ConfigDict

from .bikram_sambat import bs_to_gregorian, gregorian_to_bs, get_bs_month_name
from .tithi.tithi_boundaries import find_next_tithi
from .tithi.tithi_core import is_purnima, is_amavasya

# Compatibility constants for existing code
PAKSHA_SHUKLA = "shukla"
PAKSHA_KRISHNA = "krishna"


def find_purnima(after: date, bs_month: int = None, max_search_days: int = 45):
    """Compatibility wrapper: Find next Purnima (Shukla 15)."""
    from datetime import datetime, timezone
    dt = datetime(after.year, after.month, after.day, tzinfo=timezone.utc)
    return find_next_tithi(15, "shukla", dt, within_days=max_search_days)


def find_amavasya(after: date, bs_month: int = None, max_search_days: int = 45):
    """Compatibility wrapper: Find next Amavasya (Krishna 15)."""
    from datetime import datetime, timezone
    dt = datetime(after.year, after.month, after.day, tzinfo=timezone.utc)
    return find_next_tithi(15, "krishna", dt, within_days=max_search_days)


class DateRange(NamedTuple):
    """
    Represents a festival date range.
    
    Attributes:
        start: First day of the festival
        end: Last day of the festival
        year: The BS year this calculation is for
    """
    start: date
    end: date
    year: int
    
    @property
    def duration_days(self) -> int:
        """Number of days the festival spans."""
        return (self.end - self.start).days + 1
    
    def overlaps(self, other_date: date) -> bool:
        """Check if a date falls within this range."""
        return self.start <= other_date <= self.end
    
    def days_until(self, from_date: Optional[date] = None) -> int:
        """Days until the festival starts (negative if already started/passed)."""
        if from_date is None:
            from_date = date.today()
        return (self.start - from_date).days


class FestivalCalculationError(Exception):
    """Raised when a festival date cannot be calculated."""
    pass


# Calendar rule types
CalendarType = Literal["bikram_sambat", "nepal_sambat", "tibetan", "solar", "lunar"]


class CalendarRule(BaseModel):
    """
    Defines how to calculate a festival's date.
    
    Different festivals use different rules:
    - Solar festivals: fixed day in BS month (e.g., Maghe Sankranti = Magh 1)
    - Lunar festivals: specific tithi in a month (e.g., Dashain = Ashwin Shukla 1)
    - Multi-day festivals: duration specified
    """
    calendar_type: CalendarType
    bs_month: Optional[int] = None  # 1-12, which BS month
    tithi: Optional[int] = None  # 1-15, which lunar day
    paksha: Optional[Literal["shukla", "krishna"]] = None  # Which fortnight
    solar_day: Optional[int] = None  # For solar calendar (day of month)
    duration: int = 1  # How many days
    notes: Optional[str] = None  # Any special notes
    
    model_config = ConfigDict(frozen=True)


# Festival calculation rules
# These define how to compute the date for each festival
FESTIVAL_RULES: Dict[str, CalendarRule] = {
    # Major National Festivals
    "dashain": CalendarRule(
        calendar_type="lunar",
        bs_month=6,  # Ashwin
        tithi=1,
        paksha="shukla",
        duration=15,  # Ghatasthapana to Kojagrat Purnima
        notes="Starts on Ashwin Shukla Pratipada"
    ),
    
    "tihar": CalendarRule(
        calendar_type="lunar",
        bs_month=7,  # Kartik
        tithi=14,  # Krishna Chaturdashi (Kaag Tihar)
        paksha="krishna",
        duration=5,  # Kaag Tihar to Bhai Tika
        notes="Official: Kartik Krishna 14 (Kaag Tihar Nov 7, 2026)"
    ),
    
    "holi": CalendarRule(
        calendar_type="lunar",
        bs_month=11,  # Falgun
        tithi=15,
        paksha="shukla",
        duration=2,  # Holika Dahan + Color play
        notes="Falgun Purnima"
    ),
    
    "shivaratri": CalendarRule(
        calendar_type="lunar",
        bs_month=11,  # Falgun
        tithi=14,
        paksha="krishna",
        duration=1,
        notes="Night vigil, Pashupatinath"
    ),
    
    "buddha-jayanti": CalendarRule(
        calendar_type="lunar",
        bs_month=2,  # Baisakh
        tithi=15,
        paksha="shukla",
        duration=1,
        notes="Baisakh Purnima"
    ),
    
    "teej": CalendarRule(
        calendar_type="lunar",
        bs_month=5,  # Bhadra
        tithi=3,
        paksha="shukla",
        duration=3,  # Dar Khane Din to Rishi Panchami
        notes="Haritalika Teej"
    ),
    
    "janai-purnima": CalendarRule(
        calendar_type="lunar",
        bs_month=4,  # Shrawan
        tithi=15,
        paksha="shukla",
        duration=1,
        notes="Sacred thread ceremony"
    ),
    
    # Solar Festivals
    "maghe-sankranti": CalendarRule(
        calendar_type="solar",
        bs_month=10,  # Magh
        solar_day=1,
        duration=1,
        notes="First day of Magh"
    ),
    
    "bs-new-year": CalendarRule(
        calendar_type="solar",
        bs_month=1,  # Baishakh
        solar_day=1,
        duration=1,
        notes="Nepali New Year"
    ),
    
    # Newari Festivals
    "indra-jatra": CalendarRule(
        calendar_type="lunar",
        bs_month=5,  # Bhadra
        tithi=12,
        paksha="shukla",
        duration=8,
        notes="Bhadra Shukla 12 to Ashwin Krishna 4"
    ),
    
    "gai-jatra": CalendarRule(
        calendar_type="lunar",
        bs_month=4,  # Shrawan
        tithi=1,
        paksha="krishna",
        duration=1,
        notes="Day after Janai Purnima"
    ),
    
    "bisket-jatra": CalendarRule(
        calendar_type="solar",
        bs_month=12,  # Chaitra (starts) to Baishakh (ends)
        solar_day=25,  # Approximate start, runs into new year
        duration=9,
        notes="Bhaktapur New Year festival"
    ),
    
    "mha-puja": CalendarRule(
        calendar_type="lunar",
        bs_month=7,  # Kartik
        tithi=15,
        paksha="krishna",  # Amavasya
        duration=1,
        notes="Nepal Sambat New Year"
    ),
    
    "yomari-punhi": CalendarRule(
        calendar_type="lunar",
        bs_month=9,  # Poush
        tithi=15,
        paksha="shukla",
        duration=1,
        notes="Harvest festival, Yomari making"
    ),
    
    "ghode-jatra": CalendarRule(
        calendar_type="lunar",
        bs_month=12,  # Chaitra
        tithi=15,
        paksha="krishna",
        duration=1,
        notes="Horse parade at Tundikhel"
    ),
    
    "rato-machhindranath": CalendarRule(
        calendar_type="lunar",
        bs_month=1,  # Baishakh start
        tithi=4,
        paksha="shukla",
        duration=30,  # Approximate - longest chariot festival
        notes="Month-long chariot procession"
    ),
    
    # Additional National Festivals
    "chhath": CalendarRule(
        calendar_type="lunar",
        bs_month=7,  # Kartik
        tithi=6,
        paksha="shukla",
        duration=4,  # Nahaye Khaye to Usha Arghya
        notes="Sun worship festival, mainly Terai"
    ),
    
    "lhosar": CalendarRule(
        calendar_type="lunar",
        bs_month=10,  # Magh (approximate - varies by community)
        tithi=1,
        paksha="shukla",
        duration=3,
        notes="Tibetan/Tamang/Gurung New Year"
    ),
    
    "krishna-janmashtami": CalendarRule(
        calendar_type="lunar",
        bs_month=4,  # Shrawan/Bhadra cusp
        tithi=8,
        paksha="krishna",
        duration=1,
        notes="Krishna Ashtami, Patan celebration"
    ),
    
    "ram-navami": CalendarRule(
        calendar_type="lunar",
        bs_month=12,  # Chaitra
        tithi=9,
        paksha="shukla",
        duration=1,
        notes="Rama's birthday, Janakpur celebrations"
    ),
    
    "saraswati-puja": CalendarRule(
        calendar_type="lunar",
        bs_month=10,  # Magh
        tithi=5,
        paksha="shukla",
        duration=1,
        notes="Basant Panchami, goddess of knowledge"
    ),
    
    "udhauli": CalendarRule(
        calendar_type="lunar",
        bs_month=7,  # Kartik/Mangsir
        tithi=15,
        paksha="shukla",
        duration=1,
        notes="Kirat winter migration festival"
    ),
    
    "ubhauli": CalendarRule(
        calendar_type="lunar",
        bs_month=2,  # Jestha (celebrated when Baishakh ends)
        tithi=1,
        paksha="shukla",
        duration=1,
        notes="Kirat spring migration festival"
    ),
    
    "nag-panchami": CalendarRule(
        calendar_type="lunar",
        bs_month=4,  # Shrawan
        tithi=5,
        paksha="shukla",
        duration=1,
        notes="Serpent worship day"
    ),
    
    "fagu-purnima": CalendarRule(
        calendar_type="lunar",
        bs_month=11,  # Falgun
        tithi=15,
        paksha="shukla",
        duration=1,
        notes="Full moon Holi in hills"
    ),
}


def calculate_festival_date(
    festival_id: str,
    gregorian_year: int,
    use_overrides: bool = True
) -> DateRange:
    """
    Calculate the Gregorian dates for a festival in a given year.
    
    This is the main entry point for festival date calculation. It handles
    all calendar types and calculation rules.
    
    Args:
        festival_id: The festival identifier (e.g., "dashain", "tihar")
        gregorian_year: The Gregorian year to calculate for
    
    Returns:
        DateRange with start, end, and year
    
    Raises:
        FestivalCalculationError: If the festival cannot be calculated
        KeyError: If the festival_id is not recognized
    
    Examples:
        >>> dashain = calculate_festival_date("dashain", 2026)
        >>> print(dashain.start)  # Returns October 2, 2026
        
        >>> tihar = calculate_festival_date("tihar", 2026)
        >>> print(tihar.duration_days)  # Returns 5
    """
    if use_overrides:
        # Authoritative overrides (official dates) when available
        try:
            from .overrides import get_festival_override
            override_date = get_festival_override(festival_id, gregorian_year)
            if override_date:
                try:
                    rule = get_festival_rule(festival_id)
                    duration = rule.duration
                except Exception:
                    duration = 1
                end_date = override_date + timedelta(days=duration - 1)
                return DateRange(start=override_date, end=end_date, year=gregorian_year)
        except Exception:
            # If overrides aren't available, fall back to calculations
            pass
    
    rule = get_festival_rule(festival_id)
    
    try:
        if rule.calendar_type == "solar":
            return _calculate_solar_festival(festival_id, gregorian_year, rule)
        elif rule.calendar_type in ("lunar", "bikram_sambat", "nepal_sambat"):
            return _calculate_lunar_festival(festival_id, gregorian_year, rule)
        else:
            raise FestivalCalculationError(f"Unsupported calendar type: {rule.calendar_type}")
    except Exception as e:
        raise FestivalCalculationError(f"Failed to calculate {festival_id} for {gregorian_year}: {e}")


def _calculate_solar_festival(festival_id: str, gregorian_year: int, rule: CalendarRule) -> DateRange:
    """Calculate a solar calendar festival date."""
    
    # Solar festivals are fixed to BS calendar days
    # First, determine which BS year corresponds to this Gregorian year
    # BS year typically starts in April, so for a festival in Jan-March,
    # use previous April's BS year
    
    if rule.bs_month is None or rule.solar_day is None:
        raise FestivalCalculationError(f"Solar festival {festival_id} missing month or day")
    
    # BS year is roughly gregorian_year + 57 (before April) or + 56 (after April)
    # But we need to check which month
    bs_year = gregorian_year + 56  # Starting estimate (for April-December)
    
    if rule.bs_month >= 10:  # Jan-March festivals (Magh, Falgun, Chaitra)
        bs_year = gregorian_year + 56  # Festival in early year uses later BS year
    else:
        bs_year = gregorian_year + 57
    
    # For festivals near year boundaries, adjust
    if rule.bs_month == 1:  # Baishakh (April)
        bs_year = gregorian_year + 57
    
    try:
        start_date = bs_to_gregorian(bs_year, rule.bs_month, rule.solar_day)
        end_date = start_date + timedelta(days=rule.duration - 1)
        return DateRange(start=start_date, end=end_date, year=bs_year)
    except ValueError as e:
        raise FestivalCalculationError(f"Invalid BS date for {festival_id}: {e}")


def _calculate_lunar_festival(festival_id: str, gregorian_year: int, rule: CalendarRule) -> DateRange:
    """Calculate a lunar (tithi-based) festival date."""
    
    if rule.tithi is None or rule.paksha is None or rule.bs_month is None:
        raise FestivalCalculationError(f"Lunar festival {festival_id} missing tithi, paksha, or month")
    
    # Determine search start based on BS month and Gregorian year
    # We need to find when this BS month falls in the Gregorian year
    
    # BS year calculation
    bs_year = gregorian_year + 57  # Approximate
    if rule.bs_month <= 9:  # Baishakh-Poush (April-January)
        bs_year = gregorian_year + 57
    else:  # Magh-Chaitra (January-April)
        bs_year = gregorian_year + 56
    
    # Get approximate start of the BS month
    try:
        month_start = bs_to_gregorian(bs_year, rule.bs_month, 1)
    except ValueError:
        # Try alternate year
        try:
            bs_year = gregorian_year + 56
            month_start = bs_to_gregorian(bs_year, rule.bs_month, 1)
        except ValueError:
            raise FestivalCalculationError(
                f"Cannot find BS month {rule.bs_month} in {gregorian_year}"
            )
    
    # Verify this is in the correct Gregorian year
    if month_start.year != gregorian_year:
        # Adjust BS year
        if month_start.year < gregorian_year:
            bs_year += 1
            month_start = bs_to_gregorian(bs_year, rule.bs_month, 1)
        else:
            bs_year -= 1
            month_start = bs_to_gregorian(bs_year, rule.bs_month, 1)
    
    # Search for the tithi starting from a few days before month start
    search_start = month_start - timedelta(days=5)
    
    # Convert date to datetime WITH timezone for the ephemeris-based tithi finder
    from datetime import datetime as dt_type
    search_start_dt = dt_type.combine(search_start, dt_type.min.time()).replace(tzinfo=timezone.utc)
    
    festival_start_dt = find_next_tithi(
        rule.tithi,
        rule.paksha,
        after=search_start_dt,
        within_days=45
    )
    
    # Convert back to date if we got a datetime
    if festival_start_dt is not None:
        if hasattr(festival_start_dt, 'date'):
            festival_start = festival_start_dt.date()
        else:
            festival_start = festival_start_dt
    else:
        festival_start = None
    
    if festival_start is None:
        raise FestivalCalculationError(
            f"Could not find tithi {rule.tithi} {rule.paksha} in "
            f"month {rule.bs_month} for {gregorian_year}"
        )
    
    end_date = festival_start + timedelta(days=rule.duration - 1)
    
    return DateRange(start=festival_start, end=end_date, year=bs_year)


def get_upcoming_festivals(
    from_date: date,
    days: int = 30,
    festival_ids: Optional[List[str]] = None
) -> List[Tuple[str, DateRange]]:
    """
    Get all festivals occurring within a date range.
    
    Args:
        from_date: Starting date
        days: Number of days to look ahead
        festival_ids: Optional list of specific festivals to check
    
    Returns:
        List of (festival_id, DateRange) tuples, sorted by start date
    
    Examples:
        >>> upcoming = get_upcoming_festivals(date(2026, 9, 1), days=60)
        >>> for festival_id, dates in upcoming:
        ...     print(f"{festival_id}: {dates.start}")
    """
    if festival_ids is None:
        festival_ids = list(FESTIVAL_RULES.keys())
    
    end_date = from_date + timedelta(days=days)
    results = []
    
    # Check current year and next year to catch festivals near year boundaries
    years_to_check = {from_date.year, end_date.year}
    
    for festival_id in festival_ids:
        for year in years_to_check:
            try:
                date_range = calculate_festival_date(festival_id, year)
                
                # Check if this festival falls (even partially) within our range
                if date_range.end >= from_date and date_range.start <= end_date:
                    results.append((festival_id, date_range))
            except (FestivalCalculationError, KeyError, ValueError):
                # Skip festivals that fail calculation
                continue
    
    # Sort by start date
    results.sort(key=lambda x: x[1].start)
    
    # Remove duplicates (same festival might appear from multiple years)
    seen = set()
    unique_results = []
    for festival_id, date_range in results:
        key = (festival_id, date_range.start)
        if key not in seen:
            seen.add(key)
            unique_results.append((festival_id, date_range))
    
    return unique_results


def get_festivals_on_date(target_date: date) -> List[Tuple[str, DateRange]]:
    """
    Get all festivals occurring on a specific date.
    
    Args:
        target_date: The date to check
    
    Returns:
        List of (festival_id, DateRange) tuples for festivals on that date
    
    Examples:
        >>> festivals = get_festivals_on_date(date(2026, 10, 8))
        >>> # Returns festivals like Dashain if it's ongoing
    """
    results = []
    
    for festival_id in list_all_festivals():
        try:
            date_range = calculate_festival_date(festival_id, target_date.year)
            if date_range.overlaps(target_date):
                results.append((festival_id, date_range))
        except (FestivalCalculationError, KeyError, ValueError):
            continue
    
    return results


def get_next_occurrence(festival_id: str, after_date: Optional[date] = None) -> DateRange:
    """
    Get the next occurrence of a specific festival.
    
    Args:
        festival_id: The festival identifier
        after_date: Date to search from (defaults to today)
    
    Returns:
        DateRange for the next occurrence
    
    Raises:
        FestivalCalculationError: If next occurrence cannot be found
    
    Examples:
        >>> next_dashain = get_next_occurrence("dashain")
        >>> print(f"Dashain starts: {next_dashain.start}")
    """
    if after_date is None:
        after_date = date.today()
    
    # Check current year and next 2 years
    for year in [after_date.year, after_date.year + 1, after_date.year + 2]:
        try:
            date_range = calculate_festival_date(festival_id, year)
            if date_range.start > after_date:
                return date_range
            # Also return if festival is ongoing
            if date_range.overlaps(after_date):
                return date_range
        except (FestivalCalculationError, ValueError):
            continue
    
    raise FestivalCalculationError(f"Could not find next occurrence of {festival_id}")


def list_all_festivals() -> List[str]:
    """
    Get a list of all known festival IDs.
    
    Returns:
        List of festival identifier strings
    
    Uses festival_rules.json, falling back to hardcoded rules.
    """
    try:
        from .festival_rules_loader import list_festivals
        return list_festivals()
    except Exception:
        return list(FESTIVAL_RULES.keys())


# Compatibility alias for tests
list_supported_festivals = list_all_festivals


def get_festival_rule(festival_id: str) -> CalendarRule:
    """
    Get the calculation rule for a festival.
    
    Uses festival_rules.json as primary source, falling back to
    hardcoded FESTIVAL_RULES if JSON loading fails.
    
    Args:
        festival_id: The festival identifier
    
    Returns:
        CalendarRule object
    
    Raises:
        KeyError: If festival not found
    """
    # Try JSON loader first (authoritative source)
    try:
        from .festival_rules_loader import get_festival_rule as get_rule_from_json
        return get_rule_from_json(festival_id)
    except Exception:
        pass
    
    # Fallback to hardcoded rules
    if festival_id not in FESTIVAL_RULES:
        raise KeyError(f"Unknown festival: {festival_id}")
    return FESTIVAL_RULES[festival_id]
