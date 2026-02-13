"""Julian day helper utilities for plugin conversions."""

from __future__ import annotations

from datetime import date
from math import floor


def gregorian_to_jd(value: date) -> float:
    """Convert Gregorian date (midnight) to Julian Day."""
    return value.toordinal() + 1721424.5


def jd_to_gregorian(jd: float) -> date:
    """Convert Julian Day to Gregorian date (midnight-based conversion)."""
    ordinal = int(floor(jd - 1721424.5 + 1e-9))
    return date.fromordinal(ordinal)
