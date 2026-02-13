"""
Time Utilities for Project Parva v2.0

Handles Nepal Standard Time (UTC+5:45) conversions and time calculations.

Nepal has a unique timezone offset of 5 hours and 45 minutes ahead of UTC,
which requires special handling in many datetime libraries.
"""

from datetime import datetime, date, time, timedelta, timezone
from typing import Optional

# =============================================================================
# NEPAL TIMEZONE
# =============================================================================

# Nepal Standard Time: UTC+5:45
NEPAL_UTC_OFFSET_HOURS = 5
NEPAL_UTC_OFFSET_MINUTES = 45
NEPAL_UTC_OFFSET_TOTAL_SECONDS = (NEPAL_UTC_OFFSET_HOURS * 3600) + (NEPAL_UTC_OFFSET_MINUTES * 60)

# Create timezone object
NEPAL_TZ = timezone(timedelta(hours=5, minutes=45))


# =============================================================================
# CONVERSION FUNCTIONS
# =============================================================================

def to_nepal_time(dt: datetime) -> datetime:
    """
    Convert any datetime to Nepal Standard Time (UTC+5:45).
    
    Args:
        dt: Datetime (if naive, assumes UTC)
    
    Returns:
        Datetime in Nepal Standard Time
    
    Example:
        >>> to_nepal_time(datetime(2026, 2, 6, 0, 0, tzinfo=timezone.utc))
        datetime(2026, 2, 6, 5, 45, tzinfo=NEPAL_TZ)
    """
    # If naive, assume UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    # Convert to Nepal time
    return dt.astimezone(NEPAL_TZ)


def to_utc(dt: datetime) -> datetime:
    """
    Convert any datetime to UTC.
    
    Args:
        dt: Datetime (if naive, assumes Nepal time)
    
    Returns:
        Datetime in UTC
    
    Example:
        >>> to_utc(datetime(2026, 2, 6, 5, 45, tzinfo=NEPAL_TZ))
        datetime(2026, 2, 6, 0, 0, tzinfo=timezone.utc)
    """
    # If naive, assume Nepal time
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=NEPAL_TZ)
    
    # Convert to UTC
    return dt.astimezone(timezone.utc)


def nepal_midnight(date_val: date) -> datetime:
    """
    Get midnight in Nepal time for a given date.
    
    Args:
        date_val: Date
    
    Returns:
        Datetime at midnight Nepal time
    
    Example:
        >>> nepal_midnight(date(2026, 2, 6))
        datetime(2026, 2, 6, 0, 0, tzinfo=NEPAL_TZ)
    """
    return datetime.combine(date_val, time(0, 0, 0), tzinfo=NEPAL_TZ)


def nepal_noon(date_val: date) -> datetime:
    """
    Get noon in Nepal time for a given date.
    
    Args:
        date_val: Date
    
    Returns:
        Datetime at noon Nepal time
    """
    return datetime.combine(date_val, time(12, 0, 0), tzinfo=NEPAL_TZ)


# =============================================================================
# DATE UTILITIES
# =============================================================================

def current_nepal_time() -> datetime:
    """Get current time in Nepal Standard Time."""
    return datetime.now(NEPAL_TZ)


def current_nepal_date() -> date:
    """Get current date in Nepal."""
    return current_nepal_time().date()


def nepal_date_to_utc_range(date_val: date) -> tuple[datetime, datetime]:
    """
    Get the UTC datetime range for a Nepal date.
    
    A single Nepal date spans from 18:15 UTC previous day to 18:15 UTC.
    
    Args:
        date_val: Date in Nepal
    
    Returns:
        Tuple of (start_utc, end_utc) for the Nepal date
    
    Example:
        >>> nepal_date_to_utc_range(date(2026, 2, 6))
        (datetime(2026, 2, 5, 18, 15), datetime(2026, 2, 6, 18, 15))
    """
    # Start of Nepal date in UTC
    nepal_start = nepal_midnight(date_val)
    utc_start = to_utc(nepal_start)
    
    # End of Nepal date in UTC
    nepal_end = nepal_midnight(date_val + timedelta(days=1))
    utc_end = to_utc(nepal_end)
    
    return (utc_start, utc_end)


# =============================================================================
# DECIMAL TIME CONVERSIONS
# =============================================================================

def hours_to_hms(decimal_hours: float) -> tuple[int, int, int]:
    """
    Convert decimal hours to hours, minutes, seconds.
    
    Args:
        decimal_hours: Time as decimal hours (e.g., 5.75 = 5:45:00)
    
    Returns:
        Tuple of (hours, minutes, seconds)
    """
    total_seconds = int(decimal_hours * 3600)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return (hours, minutes, seconds)


def hms_to_hours(hours: int, minutes: int, seconds: int = 0) -> float:
    """
    Convert hours, minutes, seconds to decimal hours.
    
    Args:
        hours: Hours
        minutes: Minutes
        seconds: Seconds (default 0)
    
    Returns:
        Time as decimal hours
    """
    return hours + minutes / 60.0 + seconds / 3600.0


# =============================================================================
# JULIAN DAY UTILITIES (for compatibility)
# =============================================================================

def datetime_to_jd_fraction(dt: datetime) -> float:
    """
    Get the fractional day part (time of day as fraction of 24 hours).
    
    NOTE: This returns time-of-day fraction (0-1), NOT the fractional JD.
    For JD calculation, use swiss_eph.get_julian_day() which handles
    the full conversion including the noon epoch.
    
    Args:
        dt: Datetime
    
    Returns:
        Time of day as fraction (0.0 = midnight, 0.5 = noon, 1.0 = end of day)
    """
    hours = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
    return hours / 24.0


def jd_to_nepal_datetime(jd: float) -> datetime:
    """
    Convert Julian Day to Nepal datetime.
    
    Args:
        jd: Julian Day Number
    
    Returns:
        Datetime in Nepal time
    """
    # Import here to avoid circular import
    from .swiss_eph import julian_day_to_datetime
    
    utc_dt = julian_day_to_datetime(jd)
    return to_nepal_time(utc_dt)
