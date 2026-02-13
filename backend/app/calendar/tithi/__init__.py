"""
Tithi Module for Project Parva v2.0

Provides complete tithi calculation functionality using Swiss Ephemeris.
"""

from .tithi_core import (
    calculate_tithi,
    calculate_tithi_at_sunrise,
    get_tithi_name,
    tithi_at_time,
    is_same_tithi,
    is_purnima,
    is_amavasya,
    is_ekadashi,
    is_chaturdashi,
    is_ashtami,
    format_tithi,
    format_tithi_short,
    TITHI_NAMES,
)

from ..ephemeris.positions import get_tithi_angle
from datetime import datetime, date, timezone
from typing import Optional

from .tithi_boundaries import (
    find_tithi_end,
    find_tithi_start,
    get_tithi_window,
    find_next_tithi,
    find_tithi_in_month,
    get_tithis_in_range,
    get_tithi_duration,
)

from .tithi_udaya import (
    get_udaya_tithi,
    get_tithi_for_date,
    get_official_tithi,
    detect_vriddhi,
    detect_ksheepana,
)


# =============================================================================
# COMPATIBILITY HELPERS (for routes.py and legacy code)
# =============================================================================

def get_paksha(tithi_num: int) -> str:
    """
    Get paksha (fortnight) from tithi number.
    
    Tithis 1-15 are Shukla (bright), 16-30 are Krishna (dark).
    But our new module uses 1-15 for each paksha separately.
    """
    # Allow date/datetime inputs for compatibility
    if isinstance(tithi_num, (date, datetime)):
        info = calculate_tithi(tithi_num)
        return info["paksha"]
    if tithi_num <= 15:
        return "shukla"
    return "krishna"


def calculate_moon_phase(target_date: date) -> float:
    """
    Calculate moon phase fraction using elongation angle.
    
    Returns:
        0.0 = new moon, 0.5 = full moon, 1.0 = next new moon
    """
    if isinstance(target_date, datetime):
        dt = target_date
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    angle = get_tithi_angle(dt) % 360.0
    return angle / 360.0


def find_purnima(after_date: date) -> Optional[datetime]:
    """Find next Purnima (full moon) moment after a date."""
    if isinstance(after_date, datetime):
        start = after_date
    else:
        start = datetime.combine(after_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    start_dt = find_next_tithi(15, "shukla", start)
    if start_dt is None:
        return None
    return find_tithi_end(start_dt)


def find_amavasya(after_date: date) -> Optional[datetime]:
    """Find next Amavasya (new moon) moment after a date."""
    if isinstance(after_date, datetime):
        start = after_date
    else:
        start = datetime.combine(after_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    start_dt = find_next_tithi(15, "krishna", start)
    if start_dt is None:
        return None
    return find_tithi_end(start_dt)


def is_auspicious_tithi(tithi_num: int) -> bool:
    """Return True for traditionally auspicious tithis."""
    return tithi_num in {2, 3, 5, 7, 10, 11, 12, 13, 15}


# Compatibility constants for tests/legacy usage
PAKSHA_SHUKLA = "shukla"
PAKSHA_KRISHNA = "krishna"


def _moon_phase_from_angle(angle: float) -> str:
    """
    Map elongation angle (0-360) to a descriptive moon phase name.
    Uses standard phase boundaries at 0, 90, 180, 270 degrees.
    """
    angle = angle % 360.0
    # Snap near exact phases with day-level tolerance.
    # A calendar date can represent any time in the day, so we keep wider windows.
    if angle < 12.0 or angle >= 348.0:
        return "New Moon"
    if 78.0 <= angle <= 102.0:
        return "First Quarter"
    if 168.0 <= angle <= 192.0:
        return "Full Moon"
    if 258.0 <= angle <= 282.0:
        return "Last Quarter"
    # Phase ranges
    if angle < 90.0:
        return "Waxing Crescent"
    if angle < 180.0:
        return "Waxing Gibbous"
    if angle < 270.0:
        return "Waning Gibbous"
    return "Waning Crescent"


def _moon_phase_from_tithi(tithi_num: int, paksha: str) -> str:
    """
    Map tithi + paksha to a phase name for fallback cases.
    """
    if tithi_num == 15 and paksha == "shukla":
        return "Full Moon"
    if tithi_num == 15 and paksha == "krishna":
        return "New Moon"
    if paksha == "shukla":
        return "Waxing Crescent" if tithi_num <= 7 else "Waxing Gibbous"
    return "Waning Gibbous" if tithi_num <= 7 else "Waning Crescent"


def get_moon_phase_name(date_or_tithi) -> str:
    """
    Get descriptive moon phase name from date/datetime or tithi.
    
    Uses ephemeris elongation when a datetime/date is provided.
    """
    from datetime import date as date_type, datetime, timezone
    
    if isinstance(date_or_tithi, (date_type, datetime)):
        if isinstance(date_or_tithi, date_type) and not isinstance(date_or_tithi, datetime):
            # Date-only calls should be stable and day-level friendly.
            # Use midday angle for clear full/new moon detection, then tithi fallback.
            dt = datetime.combine(date_or_tithi, datetime.min.time()).replace(tzinfo=timezone.utc)
            dt = dt.replace(hour=12)
            phase_name = _moon_phase_from_angle(get_tithi_angle(dt))
            if phase_name in {"New Moon", "Full Moon"}:
                return phase_name
            info = calculate_tithi(dt)
            return _moon_phase_from_tithi(info["display_number"], info["paksha"])

        dt = date_or_tithi
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        angle = get_tithi_angle(dt)
        return _moon_phase_from_angle(angle)
    
    # Fallback: treat input as tithi number (1-15 or 1-30)
    tithi_num = int(date_or_tithi)
    paksha = "shukla" if tithi_num <= 15 else "krishna"
    if tithi_num > 15:
        tithi_num = tithi_num - 15
    return _moon_phase_from_tithi(tithi_num, paksha)


__all__ = [
    # Core
    "calculate_tithi",
    "calculate_tithi_at_sunrise",
    "get_tithi_name",
    "tithi_at_time",
    "is_same_tithi",
    "is_purnima",
    "is_amavasya",
    "is_ekadashi",
    "is_chaturdashi",
    "is_ashtami",
    "format_tithi",
    "format_tithi_short",
    "TITHI_NAMES",
    # Boundaries
    "find_tithi_end",
    "find_tithi_start",
    "get_tithi_window",
    "find_next_tithi",
    "find_tithi_in_month",
    "get_tithis_in_range",
    "get_tithi_duration",
    # Udaya
    "get_udaya_tithi",
    "get_tithi_for_date",
    "get_official_tithi",
    "calculate_tithi_at_sunrise",
    "detect_vriddhi",
    "detect_ksheepana",
    # Compatibility
    "get_paksha",
    "get_moon_phase_name",
    "calculate_moon_phase",
    "find_purnima",
    "find_amavasya",
    "is_auspicious_tithi",
    "PAKSHA_SHUKLA",
    "PAKSHA_KRISHNA",
]
