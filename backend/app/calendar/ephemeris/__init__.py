"""
Ephemeris Module for Project Parva v2.0

Provides astronomical calculations using Swiss Ephemeris (pyswisseph)
for precise tithi, nakshatra, and festival date calculations.

Technical Specifications:
- Library: pyswisseph (Swiss Ephemeris)
- Ephemeris: Swiss/Moshier (built-in, no external JPL files configured)
- Accuracy: arcsecond-level (sufficient for panchanga-grade calculations)
- Range: 13201 BCE to 17191 CE
- Ayanamsa: Lahiri (Indian Government standard)
"""

from .swiss_eph import (
    init_ephemeris,
    get_julian_day,
    get_sun_longitude,
    get_moon_longitude,
    get_ayanamsa,
    EphemerisError,
)

from .positions import (
    get_tithi_angle,
    get_nakshatra,
    get_yoga,
    calculate_elongation,
)

from .time_utils import (
    to_nepal_time,
    to_utc,
    nepal_midnight,
    NEPAL_TZ,
)

__all__ = [
    # Swiss Ephemeris wrapper
    "init_ephemeris",
    "get_julian_day",
    "get_sun_longitude",
    "get_moon_longitude",
    "get_ayanamsa",
    "EphemerisError",
    # Position calculations
    "get_tithi_angle",
    "get_nakshatra",
    "get_yoga",
    "calculate_elongation",
    # Time utilities
    "to_nepal_time",
    "to_utc",
    "nepal_midnight",
    "NEPAL_TZ",
]
