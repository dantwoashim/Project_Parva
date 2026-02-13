"""
Swiss Ephemeris Wrapper for Project Parva v2.0

Provides a clean Python interface to pyswisseph for astronomical calculations.

EPHEMERIS MODE:
- Uses pyswisseph's built-in Swiss Ephemeris (Moshier algorithm)
- NOT using external JPL DE431 files (would require swe.set_ephe_path())
- Accuracy: ~1 arcsecond for planets, ~3 arcseconds for Moon
- Sufficient for tithi/nakshatra calculations (12° increments)

AYANAMSA: Lahiri (Chitrapaksha) - Indian Government standard

Author: Project Parva
Created: February 2026
"""

from datetime import datetime, date, timezone, timedelta
from typing import Optional, Tuple, TYPE_CHECKING
import swisseph as swe

if TYPE_CHECKING:
    from app.engine.ephemeris_config import EphemerisConfig

# =============================================================================
# CONSTANTS
# =============================================================================

# Kathmandu coordinates for local calculations
LAT_KATHMANDU = 27.7172  # °N
LON_KATHMANDU = 85.3240  # °E
ALT_KATHMANDU = 1400.0   # meters above sea level

# Nepal timezone offset
NEPAL_UTC_OFFSET_HOURS = 5
NEPAL_UTC_OFFSET_MINUTES = 45
NEPAL_TZ = timezone(timedelta(hours=5, minutes=45))

# Celestial body constants from swisseph
SUN = swe.SUN
MOON = swe.MOON

# Calculation flags
SIDEREAL_FLAGS = swe.FLG_SIDEREAL | swe.FLG_SPEED
TROPICAL_FLAGS = swe.FLG_SPEED

# Ayanamsa modes
AYANAMSA_LAHIRI = swe.SIDM_LAHIRI

# Ephemeris info (for accurate metadata)
EPHEMERIS_MODE = "swiss_moshier"  # Built-in, not JPL DE431
EPHEMERIS_ACCURACY = "arcsecond"   # ~1-3 arcseconds, not sub-arcsecond


# =============================================================================
# EXCEPTIONS
# =============================================================================

class EphemerisError(Exception):
    """Base exception for ephemeris calculation errors."""
    pass


class EphemerisRangeError(EphemerisError):
    """Raised when date is outside ephemeris range."""
    pass


class TimezoneError(EphemerisError):
    """Raised when timezone handling fails."""
    pass


# =============================================================================
# INITIALIZATION
# =============================================================================

_initialized = False


def init_ephemeris(ayanamsa: int = AYANAMSA_LAHIRI) -> None:
    """
    Initialize Swiss Ephemeris with specified ayanamsa.
    
    Args:
        ayanamsa: Ayanamsa mode (default: Lahiri)
    
    Note:
        We use pyswisseph's built-in Moshier ephemeris (no external files).
        For JPL DE431 accuracy, you would need swe.set_ephe_path() pointing
        to downloaded ephemeris files.
    """
    global _initialized
    
    # Set sidereal mode with Lahiri ayanamsa
    swe.set_sid_mode(ayanamsa)
    
    # Note: NOT setting swe.set_ephe_path() - using built-in Moshier
    # This is honest about what we're actually using
    
    _initialized = True


def _ensure_initialized() -> None:
    """Ensure ephemeris is initialized before calculations."""
    global _initialized
    if not _initialized:
        init_ephemeris()


def get_ephemeris_info() -> dict:
    """Return metadata about the ephemeris mode in use."""
    from app.engine.ephemeris_config import get_ephemeris_config

    cfg = get_ephemeris_config()
    return {
        "mode": EPHEMERIS_MODE,
        "accuracy": EPHEMERIS_ACCURACY,
        "ayanamsa": cfg.ayanamsa,
        "coordinate_system": cfg.coordinate_system,
        "library": "pyswisseph",
        "notes": "Using built-in Swiss/Moshier ephemeris. For higher accuracy, configure JPL DE431.",
    }


# =============================================================================
# JULIAN DAY CALCULATIONS
# =============================================================================

def _ensure_utc(dt: datetime) -> datetime:
    """
    Convert datetime to UTC. Raises if naive datetime provided.
    
    Args:
        dt: Datetime with timezone info
    
    Returns:
        Datetime in UTC
    
    Raises:
        TimezoneError: If datetime is naive (no tzinfo)
    """
    if dt.tzinfo is None:
        raise TimezoneError(
            f"Datetime must have timezone info. Got naive datetime: {dt}. "
            "Use datetime(..., tzinfo=timezone.utc) or provide timezone."
        )
    
    # Convert to UTC
    return dt.astimezone(timezone.utc)


def get_julian_day(dt: datetime) -> float:
    """
    Convert datetime to Julian Day Number.
    
    IMPORTANT: The datetime MUST have timezone info. Naive datetimes will
    raise an error to prevent silent calculation errors.
    
    Args:
        dt: Datetime with timezone (will be converted to UTC)
    
    Returns:
        Julian Day Number as float
    
    Raises:
        TimezoneError: If datetime is naive (no tzinfo)
    
    Example:
        >>> from datetime import timezone
        >>> get_julian_day(datetime(2026, 2, 6, 12, 0, 0, tzinfo=timezone.utc))
        2461046.0
    """
    # Convert to UTC first - this is critical for correct JD
    utc_dt = _ensure_utc(dt)
    
    # Extract UTC components
    year = utc_dt.year
    month = utc_dt.month
    day = utc_dt.day
    hour = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    
    # Use Swiss Ephemeris Julian Day calculation
    jd = swe.julday(year, month, day, hour)
    
    return jd


def julian_day_to_datetime(jd: float) -> datetime:
    """
    Convert Julian Day Number back to datetime (UTC).
    
    Args:
        jd: Julian Day Number
    
    Returns:
        Datetime in UTC (always has tzinfo=timezone.utc)
    """
    year, month, day, hour = swe.revjul(jd)
    
    # Convert fractional hour to h/m/s
    hours = int(hour)
    minutes = int((hour - hours) * 60)
    seconds = int(((hour - hours) * 60 - minutes) * 60)
    
    return datetime(year, month, day, hours, minutes, seconds, tzinfo=timezone.utc)


# =============================================================================
# PLANETARY POSITIONS
# =============================================================================

def get_sun_longitude(
    dt: datetime,
    sidereal: Optional[bool] = None,
    config: Optional["EphemerisConfig"] = None,
) -> float:
    """
    Get Sun's ecliptic longitude.
    
    Args:
        dt: Datetime with timezone (converted to UTC internally)
        sidereal: If True, return sidereal longitude (with ayanamsa correction)
                 If False, return tropical longitude
    
    Returns:
        Longitude in degrees (0-360)
    
    Example:
        >>> get_sun_longitude(datetime(2026, 2, 6, 6, 0, tzinfo=timezone.utc))
        296.5  # Sun in Makara (Capricorn) rashi
    """
    _ensure_initialized()
    
    jd = get_julian_day(dt)
    from app.engine.ephemeris_config import get_ephemeris_config

    cfg = config or get_ephemeris_config()
    use_sidereal = sidereal if sidereal is not None else cfg.coordinate_system == "sidereal"
    if use_sidereal:
        swe.set_sid_mode(cfg.ayanamsa_code)
    flags = SIDEREAL_FLAGS if use_sidereal else TROPICAL_FLAGS
    
    try:
        result = swe.calc_ut(jd, SUN, flags)
        longitude = result[0][0]  # First element is longitude
        return longitude % 360
    except Exception as e:
        raise EphemerisError(f"Failed to calculate Sun position: {e}")


def get_moon_longitude(
    dt: datetime,
    sidereal: Optional[bool] = None,
    config: Optional["EphemerisConfig"] = None,
) -> float:
    """
    Get Moon's ecliptic longitude.
    
    Args:
        dt: Datetime with timezone (converted to UTC internally)
        sidereal: If True, return sidereal longitude (with ayanamsa correction)
                 If False, return tropical longitude
    
    Returns:
        Longitude in degrees (0-360)
    """
    _ensure_initialized()
    
    jd = get_julian_day(dt)
    from app.engine.ephemeris_config import get_ephemeris_config

    cfg = config or get_ephemeris_config()
    use_sidereal = sidereal if sidereal is not None else cfg.coordinate_system == "sidereal"
    if use_sidereal:
        swe.set_sid_mode(cfg.ayanamsa_code)
    flags = SIDEREAL_FLAGS if use_sidereal else TROPICAL_FLAGS
    
    try:
        result = swe.calc_ut(jd, MOON, flags)
        longitude = result[0][0]
        return longitude % 360
    except Exception as e:
        raise EphemerisError(f"Failed to calculate Moon position: {e}")


def get_sun_moon_positions(
    dt: datetime,
    sidereal: Optional[bool] = None,
    config: Optional["EphemerisConfig"] = None,
) -> Tuple[float, float]:
    """
    Get both Sun and Moon positions in a single call (efficiency).
    
    Args:
        dt: Datetime with timezone
        sidereal: If True, return sidereal longitudes
    
    Returns:
        Tuple of (sun_longitude, moon_longitude) in degrees
    """
    _ensure_initialized()
    
    jd = get_julian_day(dt)
    from app.engine.ephemeris_config import get_ephemeris_config

    cfg = config or get_ephemeris_config()
    use_sidereal = sidereal if sidereal is not None else cfg.coordinate_system == "sidereal"
    if use_sidereal:
        swe.set_sid_mode(cfg.ayanamsa_code)
    flags = SIDEREAL_FLAGS if use_sidereal else TROPICAL_FLAGS
    
    try:
        sun_result = swe.calc_ut(jd, SUN, flags)
        moon_result = swe.calc_ut(jd, MOON, flags)
        
        sun_long = sun_result[0][0] % 360
        moon_long = moon_result[0][0] % 360
        
        return (sun_long, moon_long)
    except Exception as e:
        raise EphemerisError(f"Failed to calculate positions: {e}")


# =============================================================================
# AYANAMSA
# =============================================================================

def get_ayanamsa(dt: datetime) -> float:
    """
    Get the ayanamsa value (precession correction) for a given date.
    
    The ayanamsa is the difference between tropical and sidereal zodiacs.
    It increases by approximately 1° every 72 years.
    
    Args:
        dt: Datetime with timezone
    
    Returns:
        Ayanamsa in degrees
    """
    _ensure_initialized()
    
    jd = get_julian_day(dt)
    
    try:
        ayanamsa = swe.get_ayanamsa_ut(jd)
        return ayanamsa
    except Exception as e:
        raise EphemerisError(f"Failed to get ayanamsa: {e}")


# =============================================================================
# SUNRISE/SUNSET (for Udaya Tithi)
# =============================================================================

def calculate_sunrise(
    date_val: date,
    latitude: float = LAT_KATHMANDU,
    longitude: float = LON_KATHMANDU,
    altitude: float = ALT_KATHMANDU
) -> datetime:
    """
    Calculate sunrise time for a given location.
    
    Args:
        date_val: Date to calculate sunrise for
        latitude: Location latitude (default: Kathmandu)
        longitude: Location longitude (default: Kathmandu)
        altitude: Altitude in meters (default: Kathmandu)
    
    Returns:
        Datetime of sunrise in UTC (with tzinfo=timezone.utc)
    
    Raises:
        EphemerisError: If sunrise calculation fails (no fallback)
    
    Example:
        >>> calculate_sunrise(date(2026, 2, 6))
        datetime(2026, 2, 6, 0, 56, 30, tzinfo=timezone.utc)  # ~6:41 AM Nepal
    """
    _ensure_initialized()
    
    # Get Julian Day for midnight UTC of the date
    # For Nepal (UTC+5:45), local midnight is previous day ~18:15 UTC
    # But we want sunrise which is around 6 AM local = 0:15 UTC same day
    jd_start = swe.julday(date_val.year, date_val.month, date_val.day, 0.0)
    
    # Calculate sunrise using Swiss Ephemeris
    # Signature: rise_trans(tjdut, body, rsmi, geopos, atpress=0.0, attemp=0.0, flags=FLG_SWIEPH)
    try:
        # rsmi: swe.CALC_RISE = 1 for sunrise
        # geopos: (longitude, latitude, altitude)
        result = swe.rise_trans(
            jd_start,                          # tjdut
            SUN,                               # body
            swe.CALC_RISE | swe.BIT_DISC_CENTER,  # rsmi (combined flags)
            (longitude, latitude, altitude),   # geopos
            0.0,                               # atpress (default)
            0.0,                               # attemp (default)
        )
        
        # result is (res_flag, tret_tuple)
        # res_flag: 0 = found, -2 = circumpolar
        # tret_tuple[0] = JD of event
        if result[0] < 0:
            raise EphemerisError(
                f"Sunrise calculation failed for {date_val} at ({latitude}, {longitude}): "
                f"Swiss Ephemeris error code {result[0]} (possibly circumpolar)"
            )
        
        jd_sunrise = result[1][0]  # First element of tret tuple
        return julian_day_to_datetime(jd_sunrise)
        
    except Exception as e:
        # NO FALLBACK - raise the error so callers know calculation failed
        # A wrong sunrise time would corrupt udaya tithi calculations
        raise EphemerisError(
            f"Sunrise calculation failed for {date_val} at ({latitude}, {longitude}): {e}"
        )


def calculate_sunset(
    date_val: date,
    latitude: float = LAT_KATHMANDU,
    longitude: float = LON_KATHMANDU,
    altitude: float = ALT_KATHMANDU
) -> datetime:
    """
    Calculate sunset time for a given location.
    
    Args:
        date_val: Date to calculate sunset for
        latitude: Location latitude (default: Kathmandu)
        longitude: Location longitude (default: Kathmandu)
        altitude: Altitude in meters (default: Kathmandu)
    
    Returns:
        Datetime of sunset in UTC (with tzinfo=timezone.utc)
    
    Raises:
        EphemerisError: If sunset calculation fails
    """
    _ensure_initialized()
    
    jd_start = swe.julday(date_val.year, date_val.month, date_val.day, 12.0)
    
    try:
        result = swe.rise_trans(
            jd_start,                          # tjdut
            SUN,                               # body
            swe.CALC_SET | swe.BIT_DISC_CENTER,   # rsmi (combined flags)
            (longitude, latitude, altitude),   # geopos
            0.0,                               # atpress (default)
            0.0,                               # attemp (default)
        )
        
        if result[0] < 0:
            raise EphemerisError(
                f"Sunset calculation failed for {date_val}: error code {result[0]}"
            )
        
        jd_sunset = result[1][0]  # First element of tret tuple
        return julian_day_to_datetime(jd_sunset)
        
    except Exception as e:
        raise EphemerisError(f"Sunset calculation failed for {date_val}: {e}")


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def normalize_degrees(degrees: float) -> float:
    """Normalize angle to 0-360 range."""
    return degrees % 360


def degrees_to_dms(degrees: float) -> Tuple[int, int, float]:
    """Convert decimal degrees to degrees, minutes, seconds."""
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = ((degrees - d) * 60 - m) * 60
    return (d, m, s)
