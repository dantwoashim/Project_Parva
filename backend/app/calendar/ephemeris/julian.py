"""Julian day conversion helpers with no dependency on Swiss wrapper modules."""

from __future__ import annotations

from datetime import datetime, timezone

import swisseph as swe


def julian_day_to_datetime(jd: float) -> datetime:
    """Convert Julian Day Number to a timezone-aware UTC datetime."""
    year, month, day, hour = swe.revjul(jd)
    hours = int(hour)
    minutes = int((hour - hours) * 60)
    seconds = int(((hour - hours) * 60 - minutes) * 60)
    return datetime(year, month, day, hours, minutes, seconds, tzinfo=timezone.utc)
