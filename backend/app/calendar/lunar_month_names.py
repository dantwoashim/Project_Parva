"""Shared lunar month naming helpers."""

from __future__ import annotations

from datetime import datetime

from .sankranti import BS_MONTH_NAMES, get_sun_rashi_at_time


def get_lunar_month_name(purnima_time: datetime) -> str:
    """
    Return the solar-rashi based lunar month name for a Purnima moment.

    This preserves the existing Project Parva convention used by both tithi
    helpers and adhik-maas detection without making those modules import each
    other.
    """
    rashi = get_sun_rashi_at_time(purnima_time)
    return BS_MONTH_NAMES[rashi]
