"""
Bikram Sambat Calendar Constants
================================

This module contains the lookup tables and constants needed for
Bikram Sambat <-> Gregorian calendar conversion.

The Bikram Sambat calendar is Nepal's official calendar. It is a solar
calendar but with month lengths that vary by year in a non-formulaic way.
Therefore, we use a lookup table approach for accurate conversion.

Coverage: 2000-2099 BS (1943-2043 AD) static lookup table.

Important: static lookup coverage is not the same as structured official
provenance. See app.calendar.provenance for the source-backed ranges.
"""

from datetime import date
from typing import Optional

# Bikram Sambat month names in English
BS_MONTH_NAMES = [
    "Baishakh",  # 1 - बैशाख
    "Jestha",  # 2 - जेठ
    "Ashadh",  # 3 - आषाढ
    "Shrawan",  # 4 - श्रावण
    "Bhadra",  # 5 - भाद्र
    "Ashwin",  # 6 - आश्विन
    "Kartik",  # 7 - कार्तिक
    "Mangsir",  # 8 - मंसिर
    "Poush",  # 9 - पौष
    "Magh",  # 10 - माघ
    "Falgun",  # 11 - फाल्गुन
    "Chaitra",  # 12 - चैत्र
]

# Bikram Sambat month names in Nepali
BS_MONTH_NAMES_NEPALI = [
    "बैशाख",
    "जेठ",
    "आषाढ",
    "श्रावण",
    "भाद्र",
    "आश्विन",
    "कार्तिक",
    "मंसिर",
    "पौष",
    "माघ",
    "फाल्गुन",
    "चैत्र",
]

# Weekday names in Nepali
WEEKDAY_NAMES_NEPALI = [
    "आइतबार",  # Sunday
    "सोमबार",  # Monday
    "मंगलबार",  # Tuesday
    "बुधबार",  # Wednesday
    "बिहीबार",  # Thursday
    "शुक्रबार",  # Friday
    "शनिबार",  # Saturday
]

# Bikram Sambat calendar data
# Format: year -> list of 12 month lengths
# Month lengths vary by year - this is the unique characteristic of BS calendar
# Start dates are computed dynamically from reference point
BS_MONTH_LENGTHS: dict[int, list[int]] = {
    # 2000s
    2000: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2001: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2002: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2003: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2004: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2005: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2006: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2007: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2008: [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 29, 31],
    2009: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    # 2010s
    2010: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2011: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2012: [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30],
    2013: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2014: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2015: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2016: [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30],
    2017: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2018: [31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2019: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    # 2020s
    2020: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2021: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2022: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
    2023: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2024: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2025: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2026: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2027: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2028: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2029: [31, 31, 32, 31, 32, 30, 30, 29, 30, 29, 30, 30],
    # 2030s
    2030: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2031: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2032: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2033: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2034: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2035: [30, 32, 31, 32, 31, 31, 29, 30, 30, 29, 29, 31],
    2036: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2037: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2038: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2039: [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30],
    # 2040s
    2040: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2041: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2042: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2043: [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30],
    2044: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2045: [31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2046: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2047: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2048: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2049: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
    # 2050s
    2050: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2051: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2052: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2053: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
    2054: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2055: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2056: [31, 31, 32, 31, 32, 30, 30, 29, 30, 29, 30, 30],
    2057: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2058: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2059: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    # 2060s
    2060: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2061: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2062: [31, 31, 31, 32, 31, 31, 29, 30, 29, 30, 29, 31],
    2063: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2064: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2065: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2066: [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 29, 31],
    2067: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2068: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2069: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    # 2070s
    2070: [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30],
    2071: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2072: [31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2073: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2074: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2075: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2076: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
    2077: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2078: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2079: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    # 2080s
    2080: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
    2081: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2082: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2083: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2084: [31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 30, 30],
    2085: [31, 32, 31, 32, 30, 31, 30, 30, 29, 30, 30, 30],
    2086: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2087: [31, 31, 32, 31, 31, 31, 30, 30, 30, 30, 30, 30],
    2088: [30, 31, 32, 32, 30, 31, 30, 30, 29, 30, 30, 30],
    2089: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    # 2090s
    2090: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2091: [31, 31, 32, 31, 31, 31, 30, 30, 29, 30, 30, 30],
    2092: [30, 31, 32, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2093: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2094: [31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 30, 30],
    2095: [31, 31, 32, 31, 31, 31, 30, 29, 30, 30, 30, 30],
    2096: [30, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2097: [31, 32, 31, 31, 31, 30, 30, 30, 29, 30, 30, 30],
    2098: [31, 31, 32, 31, 31, 31, 29, 30, 29, 30, 29, 31],
    2099: [31, 31, 32, 31, 31, 31, 30, 29, 29, 30, 30, 31],
}

# Minimum and maximum supported years
BS_MIN_YEAR = min(BS_MONTH_LENGTHS.keys())
BS_MAX_YEAR = max(BS_MONTH_LENGTHS.keys())

# Reference point from Hamro Patro public date page: 2082-01-01 BS = 2025-04-14 AD
BS_REFERENCE_START = date(2025, 4, 14)
BS_REFERENCE_YEAR = 2082


def _calculate_year_start(year: int) -> date:
    """Calculate the Gregorian start date for a BS year."""
    from datetime import timedelta

    if year == BS_REFERENCE_YEAR:
        return BS_REFERENCE_START
    elif year > BS_REFERENCE_YEAR:
        # Count days from reference forward
        days = 0
        for y in range(BS_REFERENCE_YEAR, year):
            if y in BS_MONTH_LENGTHS:
                days += sum(BS_MONTH_LENGTHS[y])
            else:
                raise ValueError(f"BS year {y} not in lookup table")
        return BS_REFERENCE_START + timedelta(days=days)
    else:
        # Count days from year up to reference backward
        days = 0
        for y in range(year, BS_REFERENCE_YEAR):
            if y in BS_MONTH_LENGTHS:
                days += sum(BS_MONTH_LENGTHS[y])
            else:
                raise ValueError(f"BS year {y} not in lookup table")
        return BS_REFERENCE_START - timedelta(days=days)


# Build the full calendar data with computed start dates
BS_CALENDAR_DATA: dict[int, tuple[list[int], date]] = {}
for _year in BS_MONTH_LENGTHS:
    BS_CALENDAR_DATA[_year] = (BS_MONTH_LENGTHS[_year], _calculate_year_start(_year))


def get_bs_year_data(year: int) -> Optional[tuple]:
    """
    Get the month lengths and start date for a BS year.

    Args:
        year: Bikram Sambat year (e.g., 2080)

    Returns:
        Tuple of (list of 12 month lengths, gregorian start date) or None if not found

    Example:
        >>> month_lengths, start_date = get_bs_year_data(2080)
        >>> month_lengths[0]  # Days in Baishakh 2080
        31
        >>> start_date
        datetime.date(2023, 4, 14)
    """
    return BS_CALENDAR_DATA.get(year)


def total_days_in_bs_year(year: int) -> int:
    """
    Calculate total days in a BS year.

    Args:
        year: Bikram Sambat year

    Returns:
        Total number of days in that year (364-366)

    Raises:
        ValueError: If year is not in the lookup table

    Example:
        >>> total_days_in_bs_year(2080)
        365
    """
    data = get_bs_year_data(year)
    if data is None:
        raise ValueError(
            f"BS year {year} is not in the supported range ({BS_MIN_YEAR}-{BS_MAX_YEAR})"
        )
    return sum(data[0])


# Tithi (lunar day) names
TITHI_NAMES = [
    "Pratipada",  # 1
    "Dwitiya",  # 2
    "Tritiya",  # 3
    "Chaturthi",  # 4
    "Panchami",  # 5
    "Shashthi",  # 6
    "Saptami",  # 7
    "Ashtami",  # 8
    "Navami",  # 9
    "Dashami",  # 10
    "Ekadashi",  # 11
    "Dwadashi",  # 12
    "Trayodashi",  # 13
    "Chaturdashi",  # 14
    "Purnima",  # 15 (Full Moon) / Amavasya (New Moon)
]

TITHI_NAMES_NEPALI = [
    "प्रतिपदा",
    "द्वितीया",
    "तृतीया",
    "चतुर्थी",
    "पञ्चमी",
    "षष्ठी",
    "सप्तमी",
    "अष्टमी",
    "नवमी",
    "दशमी",
    "एकादशी",
    "द्वादशी",
    "त्रयोदशी",
    "चतुर्दशी",
    "पूर्णिमा",  # or औंसी for Amavasya
]

# Paksha (lunar fortnight) names
PAKSHA_SHUKLA = "shukla"  # Bright/waxing fortnight (शुक्ल पक्ष)
PAKSHA_KRISHNA = "krishna"  # Dark/waning fortnight (कृष्ण पक्ष)

# Astronomical constants for tithi calculation
# Synodic month (new moon to new moon) in days
SYNODIC_MONTH = 29.530588853

# Known new moon date for reference (UTC)
# January 21, 2023 was a new moon (Amavasya)
KNOWN_NEW_MOON = date(2023, 1, 21)
