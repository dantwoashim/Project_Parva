"""Engine-level timezone helpers.

Rule: internal computation runs on timezone-aware UTC datetimes.
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone

from app.calendar.ephemeris.time_utils import NEPAL_TZ


def ensure_utc(dt: datetime | date) -> datetime:
    """Normalize date/datetime to timezone-aware UTC datetime."""
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return datetime.combine(dt, time.min, tzinfo=timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def to_npt(dt: datetime | date) -> datetime:
    """Convert date/datetime to Nepal time (UTC+5:45)."""
    return ensure_utc(dt).astimezone(NEPAL_TZ)


def from_npt(dt: datetime | date) -> datetime:
    """Interpret input as Nepal time and convert to UTC."""
    if isinstance(dt, date) and not isinstance(dt, datetime):
        local = datetime.combine(dt, time.min, tzinfo=NEPAL_TZ)
    elif isinstance(dt, datetime) and dt.tzinfo is None:
        local = dt.replace(tzinfo=NEPAL_TZ)
    else:
        local = dt
    return local.astimezone(timezone.utc)
