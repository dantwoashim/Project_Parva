"""
Panchanga (Five-Element Almanac) for Project Parva v2.0

A panchanga is the traditional Hindu/Nepali almanac containing five elements:
1. Tithi - Lunar day (1-30)
2. Nakshatra - Lunar mansion (1-27)
3. Yoga - Sun-Moon combination (1-27)
4. Karana - Half-tithi (1-60 per month)
5. Vaara - Weekday (1-7)

This module provides complete panchanga calculation for any date using
Swiss Ephemeris for precise astronomical computations.
"""

from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any, Optional

from .ephemeris.swiss_eph import (
    calculate_sunrise,
    LAT_KATHMANDU,
    LON_KATHMANDU,
    get_ephemeris_info,
)
from .ephemeris.positions import (
    get_tithi_angle,
    get_nakshatra,
    get_yoga,
    get_karana,
    get_vaara,
    get_sun_rashi,
    get_moon_rashi,
    get_sun_moon_positions,
)
from .ephemeris.time_utils import (
    to_nepal_time,
    NEPAL_TZ,
)
from .tithi.tithi_core import (
    calculate_tithi,
    get_tithi_name,
    TITHI_NAMES,
)
from .tithi.tithi_boundaries import find_tithi_end
from .tithi.tithi_udaya import get_udaya_tithi


# =============================================================================
# PANCHANGA CALCULATION
# =============================================================================

def get_panchanga(
    date_val: date,
    latitude: float = LAT_KATHMANDU,
    longitude: float = LON_KATHMANDU
) -> Dict[str, Any]:
    """
    Calculate complete panchanga (5 elements) for a date.
    
    All calculations are done for sunrise at the specified location,
    following traditional udaya tithi principles.
    
    Args:
        date_val: Date to calculate panchanga for
        latitude: Location latitude (default: Kathmandu)
        longitude: Location longitude (default: Kathmandu)
    
    Returns:
        Dictionary with complete panchanga information:
        - date: The date
        - sunrise: Sunrise time
        - tithi: Tithi details (number, name, paksha, progress)
        - nakshatra: Nakshatra details (number, name, progress)
        - yoga: Yoga details (number, name, progress)
        - karana: Karana details (number, name)
        - vaara: Weekday details (number, sanskrit_name, english_name)
        - sun_rashi: Sun's zodiac sign
        - moon_rashi: Moon's zodiac sign
        - astrological: Additional astrological data
    
    Example:
        >>> panchanga = get_panchanga(date(2026, 2, 6))
        >>> print(panchanga['tithi']['name'])
        'Panchami'
    """
    # Calculate sunrise
    sunrise_utc = calculate_sunrise(date_val, latitude, longitude)
    sunrise_nepal = to_nepal_time(sunrise_utc)
    
    # Get tithi at sunrise (udaya tithi)
    tithi_info = calculate_tithi(sunrise_utc)
    tithi_end = find_tithi_end(sunrise_utc)
    
    # Get nakshatra
    nakshatra_num, nakshatra_name, nakshatra_progress = get_nakshatra(sunrise_utc)
    
    # Get yoga
    yoga_num, yoga_name, yoga_progress = get_yoga(sunrise_utc)
    
    # Get karana
    karana_num, karana_name = get_karana(sunrise_utc)
    
    # Get vaara (weekday)
    vaara_num, vaara_sanskrit, vaara_english = get_vaara(sunrise_utc)
    
    # Get rashis (zodiac signs)
    sun_rashi_num, sun_rashi_sanskrit, sun_rashi_english = get_sun_rashi(sunrise_utc)
    moon_rashi_num, moon_rashi_sanskrit, moon_rashi_english = get_moon_rashi(sunrise_utc)
    
    # Get raw positions
    sun_long, moon_long = get_sun_moon_positions(sunrise_utc)
    
    return {
        "date": date_val.isoformat(),
        "sunrise": {
            "utc": sunrise_utc.isoformat(),
            "local": sunrise_nepal.isoformat(),
            "local_time": sunrise_nepal.strftime("%H:%M:%S"),
        },
        "tithi": {
            "number": tithi_info["number"],
            "display_number": tithi_info["display_number"],
            "name": tithi_info["name"],
            "paksha": tithi_info["paksha"],
            "progress": round(tithi_info["progress"], 4),
            "end_time": tithi_end.isoformat(),
        },
        "nakshatra": {
            "number": nakshatra_num,
            "name": nakshatra_name,
            "progress": round(nakshatra_progress, 4),
        },
        "yoga": {
            "number": yoga_num,
            "name": yoga_name,
            "progress": round(yoga_progress, 4),
        },
        "karana": {
            "number": karana_num,
            "name": karana_name,
        },
        "vaara": {
            "number": vaara_num,
            "name_sanskrit": vaara_sanskrit,
            "name_english": vaara_english,
        },
        "sun": {
            "longitude": round(sun_long, 4),
            "rashi_number": sun_rashi_num,
            "rashi_name": sun_rashi_sanskrit,
            "rashi_english": sun_rashi_english,
        },
        "moon": {
            "longitude": round(moon_long, 4),
            "rashi_number": moon_rashi_num,
            "rashi_name": moon_rashi_sanskrit,
            "rashi_english": moon_rashi_english,
        },
        **get_ephemeris_info(),  # Add actual ephemeris mode/accuracy info
    }


def get_panchanga_summary(date_val: date) -> str:
    """
    Get a human-readable panchanga summary for a date.
    
    Args:
        date_val: Date
    
    Returns:
        Multi-line summary string
    """
    p = get_panchanga(date_val)
    
    lines = [
        f"Date: {p['date']} ({p['vaara']['name_english']})",
        f"Sunrise: {p['sunrise']['local_time']} NPT",
        "",
        f"Tithi: {p['tithi']['paksha'].capitalize()} {p['tithi']['name']} ({p['tithi']['display_number']})",
        f"Nakshatra: {p['nakshatra']['name']}",
        f"Yoga: {p['yoga']['name']}",
        f"Karana: {p['karana']['name']}",
        "",
        f"Sun: {p['sun']['rashi_english']} ({p['sun']['longitude']:.1f}°)",
        f"Moon: {p['moon']['rashi_english']} ({p['moon']['longitude']:.1f}°)",
    ]
    
    return "\n".join(lines)


# =============================================================================
# DAILY PANCHANGA RANGE
# =============================================================================

def get_panchanga_range(
    start_date: date,
    days: int = 7
) -> list:
    """
    Get panchanga for a range of dates.
    
    Args:
        start_date: First date
        days: Number of days (default 7)
    
    Returns:
        List of panchanga dictionaries
    """
    return [
        get_panchanga(start_date + timedelta(days=i))
        for i in range(days)
    ]


# =============================================================================
# AUSPICIOUS TIME HELPERS
# =============================================================================

def is_auspicious_day(panchanga: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check various auspicious (shubh) conditions.
    
    Args:
        panchanga: Result from get_panchanga()
    
    Returns:
        Dictionary of auspicious conditions
    """
    tithi = panchanga["tithi"]["display_number"]
    paksha = panchanga["tithi"]["paksha"]
    nakshatra = panchanga["nakshatra"]["name"]
    yoga = panchanga["yoga"]["name"]
    vaara = panchanga["vaara"]["number"]
    
    # Auspicious tithis for various activities
    auspicious_tithis = {2, 3, 5, 7, 10, 11, 13}  # Generally auspicious
    inauspicious_tithis = {4, 8, 14}  # Rikta tithis (generally avoided)
    
    # Auspicious nakshatras for weddings, travel, etc.
    auspicious_nakshatras = {
        "Rohini", "Mrigashira", "Pushya", "Hasta", 
        "Chitra", "Swati", "Anuradha", "Shravana", "Revati"
    }
    
    # Check conditions
    is_tithi_good = tithi in auspicious_tithis
    is_tithi_rikta = tithi in inauspicious_tithis
    is_nakshatra_good = nakshatra in auspicious_nakshatras
    is_purnima = paksha == "shukla" and tithi == 15
    is_amavasya = paksha == "krishna" and tithi == 15
    is_ekadashi = tithi == 11  # Fasting day
    
    return {
        "generally_auspicious": is_tithi_good and is_nakshatra_good and not is_tithi_rikta,
        "tithi_auspicious": is_tithi_good,
        "tithi_rikta": is_tithi_rikta,
        "nakshatra_auspicious": is_nakshatra_good,
        "is_purnima": is_purnima,
        "is_amavasya": is_amavasya,
        "is_ekadashi": is_ekadashi,
        "recommended_for": _get_recommendations(panchanga),
    }


def _get_recommendations(panchanga: Dict[str, Any]) -> list:
    """Get activity recommendations based on panchanga."""
    recommendations = []
    
    tithi = panchanga["tithi"]["display_number"]
    paksha = panchanga["tithi"]["paksha"]
    
    # Ekadashi - fasting
    if tithi == 11:
        recommendations.append("Fasting (Ekadashi vrat)")
    
    # Purnima/Amavasya - special puja
    if paksha == "shukla" and tithi == 15:
        recommendations.append("Full moon rituals, Satyanarayan puja")
    if paksha == "krishna" and tithi == 15:
        recommendations.append("Amavasya tarpan, ancestor worship")
    
    # General good days
    if tithi in {2, 3, 5, 7, 10, 13}:
        recommendations.append("New ventures, ceremonies")
    
    return recommendations
