"""
Tithi Core Calculations for Project Parva v2.0

Precise tithi calculation using Swiss Ephemeris.
Includes tithi determination, progress tracking, and display formatting.

A tithi is one of 30 lunar days in a Hindu month, determined by
the angular separation between Moon and Sun (elongation).
Each tithi spans exactly 12° of elongation.

Formula: tithi = floor(elongation / 12°) + 1
"""

from datetime import datetime, date, timedelta
from typing import Tuple, Optional, Dict, Any

from ..ephemeris.positions import (
    get_tithi_angle,
    get_tithi_number,
    get_paksha,
    get_display_tithi,
    get_tithi_progress,
    TITHI_SPAN,
)
from ..ephemeris.swiss_eph import (
    get_sun_moon_positions,
    calculate_sunrise,
    LAT_KATHMANDU,
    LON_KATHMANDU,
    EphemerisError,
)
from ..ephemeris.time_utils import (
    to_nepal_time,
    to_utc,
    NEPAL_TZ,
)


# =============================================================================
# TITHI NAMES
# =============================================================================

# Sanskrit names for tithis (both pakshas use same names 1-15)
TITHI_NAMES = [
    "Pratipada",   # 1 - First day after new/full moon
    "Dwitiya",     # 2
    "Tritiya",     # 3
    "Chaturthi",   # 4
    "Panchami",    # 5
    "Shashthi",    # 6
    "Saptami",     # 7
    "Ashtami",     # 8
    "Navami",      # 9
    "Dashami",     # 10
    "Ekadashi",    # 11 - Fasting day
    "Dwadashi",    # 12
    "Trayodashi",  # 13
    "Chaturdashi", # 14
    "Purnima",     # 15 (Shukla) - Full Moon / "Amavasya" (Krishna) - New Moon
]

# Special names for 15th tithi
TITHI_15_SHUKLA = "Purnima"     # Full Moon
TITHI_15_KRISHNA = "Amavasya"   # New Moon


# =============================================================================
# CORE TITHI CALCULATION
# =============================================================================

def calculate_tithi(dt) -> Dict[str, Any]:
    """
    Calculate complete tithi information for a given datetime.
    
    Args:
        dt: Datetime (UTC or with timezone preferred) or date object.
            If a date is provided, assumes midnight UTC for backward compatibility.
    
    Returns:
        Dictionary with tithi details:
        - number: Absolute tithi 1-30
        - display_number: Display tithi 1-15
        - paksha: "shukla" or "krishna"
        - name: Sanskrit name
        - progress: 0.0 to 1.0 progress through tithi
        - elongation: Raw elongation angle
    
    Example:
        >>> calculate_tithi(datetime(2026, 2, 6, 6, 0, 0))
        {
            'number': 20,
            'display_number': 5,
            'paksha': 'krishna',
            'name': 'Panchami',
            'progress': 0.45,
            'elongation': 233.39
        }
    """
    from datetime import timezone as tz
    
    # Convert date to datetime if needed
    if isinstance(dt, date) and not isinstance(dt, datetime):
        dt = datetime.combine(dt, datetime.min.time()).replace(tzinfo=tz.utc)
    elif isinstance(dt, datetime) and dt.tzinfo is None:
        # Add UTC timezone if missing
        dt = dt.replace(tzinfo=tz.utc)
    
    elongation = get_tithi_angle(dt)
    tithi_num = get_tithi_number(elongation)
    paksha = get_paksha(tithi_num)
    display_num = get_display_tithi(tithi_num)
    progress = get_tithi_progress(elongation)
    
    # Get name
    if display_num == 15:
        name = TITHI_15_SHUKLA if paksha == "shukla" else TITHI_15_KRISHNA
    else:
        name = TITHI_NAMES[display_num - 1]
    
    return {
        "number": tithi_num,
        "display_number": display_num,
        "paksha": paksha,
        "name": name,
        "progress": round(progress, 4),
        "elongation": round(elongation, 4),
    }


def calculate_tithi_at_sunrise(
    date_val: date,
    latitude: float = LAT_KATHMANDU,
    longitude: float = LON_KATHMANDU,
) -> Dict[str, Any]:
    """
    Convenience helper for official day-level tithi.

    Computes sunrise for the date/location and returns tithi at that moment.
    """
    sunrise_utc = calculate_sunrise(date_val, latitude, longitude)
    return calculate_tithi(sunrise_utc)


def get_tithi_name(tithi: int, paksha: str = None, language: str = "english") -> str:
    """
    Get the name of a tithi.
    
    Args:
        tithi: Tithi number 1-15 (display number)
        paksha: Optional paksha for 15th tithi naming
        language: "english" or "nepali"
    
    Returns:
        Tithi name
    """
    if tithi < 1 or tithi > 15:
        raise ValueError("tithi must be in range 1..15")

    # Backward-compat: allow get_tithi_name(1, "nepali")
    if language == "english" and paksha in {"nepali", "english"}:
        language = paksha
        paksha = None

    if tithi == 15:
        if paksha == "shukla":
            return TITHI_15_SHUKLA
        elif paksha == "krishna":
            return TITHI_15_KRISHNA
    
    if language == "nepali":
        from ..constants import TITHI_NAMES_NEPALI
        return TITHI_NAMES_NEPALI[tithi - 1]
    
    return TITHI_NAMES[tithi - 1]


# =============================================================================
# TITHI AT SPECIFIC TIME
# =============================================================================

def tithi_at_time(dt: datetime) -> Tuple[int, str, str]:
    """
    Get the tithi prevailing at a specific time.
    
    Args:
        dt: Datetime
    
    Returns:
        Tuple of (display_tithi 1-15, paksha, name)
    """
    info = calculate_tithi(dt)
    return (info["display_number"], info["paksha"], info["name"])


# =============================================================================
# TITHI COMPARISON
# =============================================================================

def is_same_tithi(dt1: datetime, dt2: datetime) -> bool:
    """
    Check if two datetimes fall in the same tithi.
    
    Args:
        dt1: First datetime
        dt2: Second datetime
    
    Returns:
        True if same absolute tithi (1-30)
    """
    elongation1 = get_tithi_angle(dt1)
    elongation2 = get_tithi_angle(dt2)
    
    tithi1 = int(elongation1 / TITHI_SPAN) + 1
    tithi2 = int(elongation2 / TITHI_SPAN) + 1
    
    return tithi1 == tithi2


def tithi_difference(dt1: datetime, dt2: datetime) -> int:
    """
    Calculate the number of tithis between two datetimes.
    
    Args:
        dt1: Start datetime
        dt2: End datetime
    
    Returns:
        Number of complete tithis between dt1 and dt2
    """
    elongation1 = get_tithi_angle(dt1)
    elongation2 = get_tithi_angle(dt2)
    
    tithi1 = int(elongation1 / TITHI_SPAN)
    tithi2 = int(elongation2 / TITHI_SPAN)
    
    return tithi2 - tithi1


# =============================================================================
# SPECIAL TITHIS
# =============================================================================

def is_purnima(dt: datetime) -> bool:
    """Check if it's Purnima (full moon, Shukla 15)."""
    info = calculate_tithi(dt)
    return info["paksha"] == "shukla" and info["display_number"] == 15


def is_amavasya(dt: datetime) -> bool:
    """Check if it's Amavasya (new moon, Krishna 15)."""
    info = calculate_tithi(dt)
    return info["paksha"] == "krishna" and info["display_number"] == 15


def is_ekadashi(dt: datetime) -> bool:
    """Check if it's Ekadashi (11th tithi, fasting day)."""
    info = calculate_tithi(dt)
    return info["display_number"] == 11


def is_chaturdashi(dt: datetime) -> bool:
    """Check if it's Chaturdashi (14th tithi)."""
    info = calculate_tithi(dt)
    return info["display_number"] == 14


def is_ashtami(dt: datetime) -> bool:
    """Check if it's Ashtami (8th tithi)."""
    info = calculate_tithi(dt)
    return info["display_number"] == 8


# =============================================================================
# LUNAR MONTH DETERMINATION
# =============================================================================

def get_lunar_month_name(elongation: float) -> str:
    """
    Get approximate lunar month name based on elongation.
    
    Note: This is a rough approximation. For accurate lunar month,
    use the sankranti-based calculation.
    
    The lunar month is named after the Purnima nakshatra:
    - If Purnima falls in Chitra nakshatra → Chaitra month
    - If Purnima falls in Vaishakha nakshatra → Vaishakha month
    etc.
    """
    # Simplified approximation based on solar position
    # In practice, this needs sankranti-based calculation
    pass  # TODO: Implement with sankranti


# =============================================================================
# TITHI FORMATTING
# =============================================================================

def format_tithi(tithi_info: Dict[str, Any], include_progress: bool = False) -> str:
    """
    Format tithi information for display.
    
    Args:
        tithi_info: Dictionary from calculate_tithi()
        include_progress: Whether to include progress percentage
    
    Returns:
        Formatted string like "Krishna Panchami" or "Shukla Ekadashi (65%)"
    """
    paksha = tithi_info["paksha"].capitalize()
    name = tithi_info["name"]
    
    if include_progress:
        progress_pct = int(tithi_info["progress"] * 100)
        return f"{paksha} {name} ({progress_pct}%)"
    
    return f"{paksha} {name}"


def format_tithi_short(tithi_info: Dict[str, Any]) -> str:
    """
    Format tithi in short form like "K5" (Krishna Panchami).
    
    Args:
        tithi_info: Dictionary from calculate_tithi()
    
    Returns:
        Short form like "S15" for Purnima, "K5" for Krishna Panchami
    """
    prefix = "S" if tithi_info["paksha"] == "shukla" else "K"
    return f"{prefix}{tithi_info['display_number']}"
