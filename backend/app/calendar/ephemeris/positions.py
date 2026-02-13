"""
Astronomical Position Calculations for Project Parva v2.0

Higher-level calculations built on Swiss Ephemeris:
- Tithi angle (elongation)
- Nakshatra (lunar mansion)
- Yoga (sun+moon combination)
- Karana (half-tithi)
"""

from datetime import datetime
from typing import Tuple, Optional

from .swiss_eph import (
    get_sun_longitude,
    get_moon_longitude,
    get_sun_moon_positions,
    EphemerisError,
)


# =============================================================================
# CONSTANTS
# =============================================================================

# Nakshatra names (27 lunar mansions)
NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Yoga names (27 yogas from sun+moon)
YOGA_NAMES = [
    "Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti"
]

# Karana names (11 karanas, some repeat)
KARANA_NAMES = [
    "Bava", "Balava", "Kaulava", "Taitila", "Garija",
    "Vanija", "Vishti", "Shakuni", "Chatushpada", "Naga", "Kimstughna"
]

# Fixed karanas (appear only once in a lunar month)
FIXED_KARANAS = ["Shakuni", "Chatushpada", "Naga", "Kimstughna"]

# Each nakshatra spans 13°20' = 13.333...°
NAKSHATRA_SPAN = 360.0 / 27.0  # 13.333...°

# Each tithi spans 12°
TITHI_SPAN = 12.0

# Each yoga spans 13°20' (same as nakshatra)
YOGA_SPAN = 360.0 / 27.0

# Each karana spans 6° (half tithi)
KARANA_SPAN = 6.0


# =============================================================================
# TITHI CALCULATIONS
# =============================================================================

def get_tithi_angle(dt: datetime) -> float:
    """
    Calculate the tithi angle (elongation between Moon and Sun).
    
    The tithi angle is: (Moon longitude - Sun longitude) mod 360
    
    Args:
        dt: Datetime (UTC recommended)
    
    Returns:
        Elongation in degrees (0-360)
    
    Note:
        Tithi number = floor(elongation / 12) + 1
    """
    sun_long, moon_long = get_sun_moon_positions(dt)
    
    # Calculate elongation (Moon ahead of Sun)
    elongation = (moon_long - sun_long) % 360
    
    return elongation


def calculate_elongation(dt: datetime) -> float:
    """
    Alias for get_tithi_angle for clarity.
    
    The elongation is the angular separation between Moon and Sun
    as viewed from Earth. It's the basis for tithi calculation.
    """
    return get_tithi_angle(dt)


def get_tithi_number(elongation: float) -> int:
    """
    Get tithi number (1-30) from elongation angle.
    
    Args:
        elongation: Moon-Sun elongation in degrees (0-360)
    
    Returns:
        Tithi number 1-30
    
    Note:
        Tithis 1-15 are Shukla (waxing), 16-30 are Krishna (waning)
    """
    return int(elongation / TITHI_SPAN) + 1


def get_paksha(tithi: int) -> str:
    """
    Get paksha (lunar fortnight) from tithi number.
    
    Args:
        tithi: Tithi number 1-30
    
    Returns:
        "shukla" (waxing, 1-15) or "krishna" (waning, 16-30)
    """
    return "shukla" if tithi <= 15 else "krishna"


def get_display_tithi(tithi: int) -> int:
    """
    Get display tithi (1-15) from absolute tithi (1-30).
    
    Args:
        tithi: Absolute tithi 1-30
    
    Returns:
        Display tithi 1-15 (restarts at 1 for Krishna paksha)
    """
    return tithi if tithi <= 15 else tithi - 15


def get_tithi_progress(elongation: float) -> float:
    """
    Get progress through current tithi (0.0 to 1.0).
    
    Args:
        elongation: Moon-Sun elongation in degrees
    
    Returns:
        Progress through tithi (0.0 = just started, 1.0 = about to end)
    """
    return (elongation % TITHI_SPAN) / TITHI_SPAN


# =============================================================================
# NAKSHATRA CALCULATIONS
# =============================================================================

def get_nakshatra(dt: datetime) -> Tuple[int, str, float]:
    """
    Calculate the nakshatra (lunar mansion) for a given time.
    
    Nakshatra is determined by Moon's sidereal longitude.
    Each nakshatra spans 13°20' (360°/27 = 13.333...°).
    
    Args:
        dt: Datetime (UTC recommended)
    
    Returns:
        Tuple of (nakshatra_number 1-27, nakshatra_name, progress 0-1)
    
    Example:
        >>> get_nakshatra(datetime(2026, 2, 6, 6, 0))
        (5, "Mrigashira", 0.65)
    """
    moon_long = get_moon_longitude(dt)
    
    # Calculate nakshatra
    nakshatra_float = moon_long / NAKSHATRA_SPAN
    nakshatra_num = int(nakshatra_float) + 1  # 1-indexed
    
    # Handle wrap-around
    if nakshatra_num > 27:
        nakshatra_num = 1
    
    progress = nakshatra_float % 1
    name = NAKSHATRA_NAMES[nakshatra_num - 1]
    
    return (nakshatra_num, name, progress)


def get_nakshatra_pada(moon_longitude: float) -> int:
    """
    Get the pada (quarter) of the nakshatra.
    
    Each nakshatra has 4 padas, each spanning 3°20'.
    
    Args:
        moon_longitude: Moon's sidereal longitude
    
    Returns:
        Pada number 1-4
    """
    pada_span = NAKSHATRA_SPAN / 4
    position_in_nakshatra = moon_longitude % NAKSHATRA_SPAN
    return int(position_in_nakshatra / pada_span) + 1


# =============================================================================
# YOGA CALCULATIONS
# =============================================================================

def get_yoga(dt: datetime) -> Tuple[int, str, float]:
    """
    Calculate the yoga for a given time.
    
    Yoga is determined by the sum of Sun and Moon longitudes.
    Each yoga spans 13°20' (same as nakshatra).
    
    Formula: yoga = ((sun_long + moon_long) mod 360) / 13.333...
    
    Args:
        dt: Datetime (UTC recommended)
    
    Returns:
        Tuple of (yoga_number 1-27, yoga_name, progress 0-1)
    
    Example:
        >>> get_yoga(datetime(2026, 2, 6, 6, 0))
        (12, "Dhruva", 0.45)
    """
    sun_long, moon_long = get_sun_moon_positions(dt)
    
    # Sum of longitudes
    total_long = (sun_long + moon_long) % 360
    
    # Calculate yoga
    yoga_float = total_long / YOGA_SPAN
    yoga_num = int(yoga_float) + 1  # 1-indexed
    
    # Handle wrap-around
    if yoga_num > 27:
        yoga_num = 1
    
    progress = yoga_float % 1
    name = YOGA_NAMES[yoga_num - 1]
    
    return (yoga_num, name, progress)


# =============================================================================
# KARANA CALCULATIONS
# =============================================================================

def get_karana(dt: datetime) -> Tuple[int, str]:
    """
    Calculate the karana for a given time.
    
    Karana is half of a tithi (6° of elongation).
    There are 11 karanas, but only 7 recur regularly.
    4 fixed karanas appear only once per lunar month.
    
    Args:
        dt: Datetime (UTC recommended)
    
    Returns:
        Tuple of (karana_number 1-60 per month, karana_name)
    """
    elongation = get_tithi_angle(dt)
    
    # There are 60 karanas in a lunar month (2 per tithi)
    karana_index = int(elongation / KARANA_SPAN)
    
    # Map to karana name
    # First karana of first tithi is Kimstughna (fixed)
    # Then rotate through Bava, Balava, Kaulava, Taitila, Garija, Vanija, Vishti
    # Last karanas are fixed: Shakuni, Chatushpada, Naga
    
    if karana_index == 0:
        name = "Kimstughna"
    elif karana_index >= 57:
        # Last 3 are fixed
        fixed_index = karana_index - 57
        name = ["Shakuni", "Chatushpada", "Naga"][fixed_index]
    else:
        # Rotating karanas (1-56 after first)
        rotating_index = (karana_index - 1) % 7
        name = KARANA_NAMES[rotating_index]
    
    return (karana_index + 1, name)


# =============================================================================
# VAARA (WEEKDAY)
# =============================================================================

VAARA_NAMES = [
    "Ravivara",    # Sunday (Sun)
    "Somavara",    # Monday (Moon)
    "Mangalavara", # Tuesday (Mars)
    "Budhavara",   # Wednesday (Mercury)
    "Guruvara",    # Thursday (Jupiter)
    "Shukravara",  # Friday (Venus)
    "Shanivara"    # Saturday (Saturn)
]

VAARA_ENGLISH = [
    "Sunday", "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday"
]


def get_vaara(dt: datetime, local_tz=None) -> Tuple[int, str, str]:
    """
    Get the vaara (weekday) for a given time.
    
    Args:
        dt: Datetime (should have timezone info)
        local_tz: Optional timezone for local weekday. If None, uses Nepal TZ.
    
    Returns:
        Tuple of (weekday 0-6, sanskrit_name, english_name)
    
    Note:
        Weekday is determined by local date, not UTC date.
        For Nepal (UTC+5:45), this matters around midnight.
    """
    from .time_utils import NEPAL_TZ
    
    # Convert to local timezone for weekday determination
    if local_tz is None:
        local_tz = NEPAL_TZ
    
    if dt.tzinfo is not None:
        local_dt = dt.astimezone(local_tz)
    else:
        # Assume UTC and convert
        from datetime import timezone
        local_dt = dt.replace(tzinfo=timezone.utc).astimezone(local_tz)
    
    weekday = local_dt.weekday()
    # Python: Monday=0, Sanskrit: Sunday=0, so adjust
    vaara_index = (weekday + 1) % 7
    
    return (vaara_index, VAARA_NAMES[vaara_index], VAARA_ENGLISH[vaara_index])


# =============================================================================
# RASHI (ZODIAC SIGN)
# =============================================================================

RASHI_NAMES = [
    "Mesha",     # Aries
    "Vrishabha", # Taurus
    "Mithuna",   # Gemini
    "Karka",     # Cancer
    "Simha",     # Leo
    "Kanya",     # Virgo
    "Tula",      # Libra
    "Vrishchika",# Scorpio
    "Dhanu",     # Sagittarius
    "Makara",    # Capricorn
    "Kumbha",    # Aquarius
    "Meena"      # Pisces
]

RASHI_ENGLISH = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]


def get_sun_rashi(dt: datetime) -> Tuple[int, str, str]:
    """
    Get the rashi (zodiac sign) of the Sun.
    
    This is used for solar month determination (sankranti-based).
    
    Args:
        dt: Datetime
    
    Returns:
        Tuple of (rashi 1-12, sanskrit_name, english_name)
    """
    sun_long = get_sun_longitude(dt)
    rashi_index = int(sun_long / 30)
    
    return (rashi_index + 1, RASHI_NAMES[rashi_index], RASHI_ENGLISH[rashi_index])


def get_moon_rashi(dt: datetime) -> Tuple[int, str, str]:
    """
    Get the rashi (zodiac sign) of the Moon.
    
    Args:
        dt: Datetime
    
    Returns:
        Tuple of (rashi 1-12, sanskrit_name, english_name)
    """
    moon_long = get_moon_longitude(dt)
    rashi_index = int(moon_long / 30)
    
    return (rashi_index + 1, RASHI_NAMES[rashi_index], RASHI_ENGLISH[rashi_index])
