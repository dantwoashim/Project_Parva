"""
Udaya Tithi Calculation for Project Parva v2.0

The "Udaya Tithi" is the tithi prevailing at sunrise — this is the
official tithi used for calendrical and religious purposes in Nepal.

In Hindu tradition, the day begins at sunrise (not midnight), so:
- The tithi at sunrise determines the religious significance of that day
- Festival dates are calculated based on udaya tithi
- If a tithi spans sunrise, it "belongs" to that day
"""

from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any, Optional

from .tithi_core import calculate_tithi, format_tithi, TITHI_NAMES
from .tithi_boundaries import find_tithi_end, get_tithi_window
from ..ephemeris.swiss_eph import calculate_sunrise, LAT_KATHMANDU, LON_KATHMANDU
from ..ephemeris.time_utils import to_nepal_time, nepal_midnight, NEPAL_TZ


# =============================================================================
# UDAYA TITHI CALCULATION
# =============================================================================

def get_udaya_tithi(
    date_val: date,
    latitude: float = LAT_KATHMANDU,
    longitude: float = LON_KATHMANDU
) -> Dict[str, Any]:
    """
    Get the tithi prevailing at sunrise (udaya tithi).
    
    This is the official tithi for the given date, used for:
    - Festival calculations
    - Panchanga (almanac) entries
    - Religious observances
    
    Args:
        date_val: Date to get udaya tithi for
        latitude: Location latitude (default: Kathmandu)
        longitude: Location longitude (default: Kathmandu)
    
    Returns:
        Dictionary with:
        - tithi: display number 1-15
        - tithi_absolute: absolute number 1-30
        - paksha: "shukla" or "krishna"
        - name: Sanskrit name
        - progress: progress at sunrise
        - sunrise: sunrise time (UTC)
        - sunrise_local: sunrise time in Nepal
        - end_time: when this tithi ends
    
    Example:
        >>> get_udaya_tithi(date(2026, 2, 6))
        {
            'tithi': 5,
            'tithi_absolute': 20,
            'paksha': 'krishna',
            'name': 'Panchami',
            'progress': 0.65,
            'sunrise': datetime(...),
            'sunrise_local': datetime(...),
            'end_time': datetime(...)
        }
    """
    # Calculate tithi at sunrise (official udaya rule)
    tithi_info = calculate_tithi_at_sunrise(date_val, latitude, longitude)
    sunrise_utc = tithi_info["sunrise"]
    sunrise_nepal = tithi_info["sunrise_local"]
    
    # Find when this tithi ends
    tithi_end = find_tithi_end(sunrise_utc)
    
    return {
        "tithi": tithi_info["display_number"],
        "tithi_absolute": tithi_info["number"],
        "paksha": tithi_info["paksha"],
        "name": tithi_info["name"],
        "progress": tithi_info["progress"],
        "elongation": tithi_info["elongation"],
        "sunrise": sunrise_utc,
        "sunrise_local": sunrise_nepal,
        "end_time": tithi_end,
        "method": "udaya_tithi",
    }


def calculate_tithi_at_sunrise(
    date_val: date,
    latitude: float = LAT_KATHMANDU,
    longitude: float = LON_KATHMANDU
) -> Dict[str, Any]:
    """
    Calculate tithi at sunrise for a given date/location.

    Args:
        date_val: Gregorian date
        latitude: latitude of observation
        longitude: longitude of observation

    Returns:
        Dict containing tithi fields from `calculate_tithi()` plus sunrise metadata.
    """
    sunrise_utc = calculate_sunrise(date_val, latitude, longitude)
    sunrise_nepal = to_nepal_time(sunrise_utc)
    tithi_info = calculate_tithi(sunrise_utc)
    return {
        **tithi_info,
        "sunrise": sunrise_utc,
        "sunrise_local": sunrise_nepal,
    }


def detect_vriddhi(
    date_val: date,
    latitude: float = LAT_KATHMANDU,
    longitude: float = LON_KATHMANDU
) -> bool:
    """
    Detect vriddhi tithi for a date.

    Vriddhi means the same absolute tithi prevails at two consecutive sunrises.
    """
    today = calculate_tithi_at_sunrise(date_val, latitude, longitude)
    tomorrow = calculate_tithi_at_sunrise(date_val + timedelta(days=1), latitude, longitude)
    return today["number"] == tomorrow["number"]


def detect_ksheepana(
    date_val: date,
    latitude: float = LAT_KATHMANDU,
    longitude: float = LON_KATHMANDU
) -> bool:
    """
    Detect ksheepana (skipped tithi) around a date.

    Ksheepana occurs when sunrise-to-sunrise tithi jump is 2, meaning one tithi
    started and ended between the two sunrises.
    """
    today = calculate_tithi_at_sunrise(date_val, latitude, longitude)
    tomorrow = calculate_tithi_at_sunrise(date_val + timedelta(days=1), latitude, longitude)
    delta = (tomorrow["number"] - today["number"]) % 30
    return delta == 2


def get_tithi_for_date(date_val: date) -> Dict[str, Any]:
    """
    Alias for get_udaya_tithi with default Kathmandu location.
    
    This is the recommended function for getting the official
    tithi for a date in Nepal.
    """
    return get_udaya_tithi(date_val)


def get_official_tithi(date_val: date) -> Dict[str, Any]:
    """
    Get the official tithi for a date (alias for get_udaya_tithi).
    """
    return get_udaya_tithi(date_val)


# =============================================================================
# TITHI CHARACTERISTICS FOR A DAY
# =============================================================================

def get_tithi_characteristics(date_val: date) -> Dict[str, Any]:
    """
    Get detailed tithi characteristics for a day.
    
    This includes:
    - Udaya tithi (at sunrise)
    - Whether tithi is ksheepana (skipped) or vriddhi (doubled)
    - Tithi window (start and end times)
    
    Args:
        date_val: Date to analyze
    
    Returns:
        Detailed tithi analysis
    """
    udaya = get_udaya_tithi(date_val)
    
    # Get tithi window
    sunrise_utc = udaya["sunrise"]
    start_time, end_time = get_tithi_window(sunrise_utc)
    
    # Check for special sunrise rules.
    is_vriddhi = detect_vriddhi(date_val)
    is_next_ksheepana = detect_ksheepana(date_val)
    
    return {
        **udaya,
        "tithi_start": start_time,
        "tithi_end": end_time,
        "duration_hours": (end_time - start_time).total_seconds() / 3600,
        "is_vriddhi": is_vriddhi,
        "next_ksheepana": is_next_ksheepana,
    }


# =============================================================================
# FESTIVAL DATE DETERMINATION
# =============================================================================

def is_festival_tithi(
    date_val: date,
    target_tithi: int,
    target_paksha: str
) -> bool:
    """
    Check if a date is the festival tithi based on udaya tithi rules.
    
    Args:
        date_val: Date to check
        target_tithi: Target tithi number 1-15
        target_paksha: "shukla" or "krishna"
    
    Returns:
        True if the udaya tithi matches the target
    
    Example:
        >>> is_festival_tithi(date(2026, 10, 2), 10, "shukla")  # Dashami check
        True
    """
    udaya = get_udaya_tithi(date_val)
    
    return (
        udaya["tithi"] == target_tithi and
        udaya["paksha"] == target_paksha
    )


def find_festival_date(
    target_tithi: int,
    target_paksha: str,
    year: int,
    month: int,
    bs_month_name: str = None
) -> Optional[date]:
    """
    Find the Gregorian date for a festival based on tithi and paksha.
    
    This uses udaya tithi rules: the date where the target tithi
    prevails at sunrise.
    
    Args:
        target_tithi: Tithi number 1-15
        target_paksha: "shukla" or "krishna"
        year: Gregorian year
        month: Gregorian month (approximate)
        bs_month_name: Optional BS month name for context
    
    Returns:
        Date when the festival tithi occurs, or None
    """
    # Search a window around the approximate month
    search_start = date(year, month, 1) - timedelta(days=5)
    search_end = date(year, month, 1) + timedelta(days=35)
    
    current_date = search_start
    while current_date <= search_end:
        if is_festival_tithi(current_date, target_tithi, target_paksha):
            return current_date
        current_date += timedelta(days=1)
    
    return None


# =============================================================================
# FORMATTING
# =============================================================================

def format_udaya_tithi(udaya: Dict[str, Any]) -> str:
    """
    Format udaya tithi for display.
    
    Args:
        udaya: Result from get_udaya_tithi()
    
    Returns:
        Formatted string like "Krishna Panchami (65% at sunrise)"
    """
    paksha = udaya["paksha"].capitalize()
    name = udaya["name"]
    progress = int(udaya["progress"] * 100)
    
    return f"{paksha} {name} ({progress}% at sunrise)"
