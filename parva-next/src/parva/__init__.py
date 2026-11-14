"""Parva - the Nepali calendar as data, with the smallest code that reads it.

    >>> import parva
    >>> parva.to_bs(date(2026, 4, 14))
    BS(year=2083, month=1, day=1)
    >>> parva.holidays.is_working_day(date(2026, 10, 19))   # Vijaya Dashami
    False

Zero-dependency:   parva.bs, parva.holidays
Needs pyswisseph:  parva.astro, parva.lunar, parva.festivals   (pip install parva-calendar[astro])
"""

from . import bs, holidays
from .bs import BS, DATA_VERSION, MAX_YEAR, MIN_YEAR, is_valid, month_days, parse, to_ad, to_bs
from .evidence import read_data
from .holidays import fiscal_year, is_working_day, next_working_day

__version__ = "1.0.0rc2"
VERSION = f"parva {__version__} / data {read_data('release.json')['version']}+{bs.DATA_SHA256[:12]}"
__all__ = [
    "BS",
    "DATA_VERSION",
    "MAX_YEAR",
    "MIN_YEAR",
    "VERSION",
    "__version__",
    "bs",
    "fiscal_year",
    "holidays",
    "is_valid",
    "is_working_day",
    "month_days",
    "next_working_day",
    "parse",
    "to_ad",
    "to_bs",
]
