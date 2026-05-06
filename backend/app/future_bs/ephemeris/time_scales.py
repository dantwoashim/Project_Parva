"""Time-scale conversion helpers for future BS astronomy code.

The current production implementation uses Swiss Ephemeris UTC/UT based helpers.
These functions centralize the approximation so future DE440 integration can
replace it without changing callers.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.calendar.ephemeris.swiss_eph import get_julian_day, julian_day_to_datetime


def utc_datetime_to_jd_ut(dt: datetime) -> float:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return get_julian_day(dt.astimezone(timezone.utc))


def jd_ut_to_utc_datetime(jd_ut: float) -> datetime:
    return julian_day_to_datetime(jd_ut).astimezone(timezone.utc)


def jd_tdb_to_jd_ut_approx(jd_tdb: float) -> float:
    # Current precision is bounded by the Swiss/Moshier fallback. Keep the
    # conversion explicit instead of pretending we have full TT/TDB modeling.
    return jd_tdb


def jd_ut_to_jd_tdb_approx(jd_ut: float) -> float:
    return jd_ut
