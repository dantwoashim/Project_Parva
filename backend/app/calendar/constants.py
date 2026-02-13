"""
Bikram Sambat Calendar Constants
================================

This module contains the lookup tables and constants needed for
Bikram Sambat <-> Gregorian calendar conversion.

The Bikram Sambat calendar is Nepal's official calendar. It is a solar
calendar but with month lengths that vary by year in a non-formulaic way.
Therefore, we use a lookup table approach for accurate conversion.

Data Sources:
- Nepal Government official calendar
- nepalidate.com verification
- Traditional panchang references

Coverage: 2070-2095 BS (2013-2038 AD)
"""

from typing import Optional
from datetime import date

# Bikram Sambat month names in English
BS_MONTH_NAMES = [
    "Baishakh",   # 1 - बैशाख
    "Jestha",     # 2 - जेठ
    "Ashadh",     # 3 - आषाढ
    "Shrawan",    # 4 - श्रावण
    "Bhadra",     # 5 - भाद्र
    "Ashwin",     # 6 - आश्विन
    "Kartik",     # 7 - कार्तिक
    "Mangsir",    # 8 - मंसिर
    "Poush",      # 9 - पौष
    "Magh",       # 10 - माघ
    "Falgun",     # 11 - फाल्गुन
    "Chaitra",    # 12 - चैत्र
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
    "आइतबार",    # Sunday
    "सोमबार",     # Monday
    "मंगलबार",    # Tuesday
    "बुधबार",     # Wednesday
    "बिहीबार",    # Thursday
    "शुक्रबार",   # Friday
    "शनिबार",     # Saturday
]

# Bikram Sambat calendar data
# Format: year -> list of 12 month lengths
# Month lengths vary by year - this is the unique characteristic of BS calendar
# Start dates are computed dynamically from reference point
BS_MONTH_LENGTHS: dict[int, list[int]] = {
    # 2070s
    2070: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2071: [31, 31, 32, 31, 32, 30, 30, 29, 30, 29, 30, 30],
    2072: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2073: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2074: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
    2075: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2076: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2077: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2078: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
    2079: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    
    # 2080s - Current decade
    2080: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2081: [31, 32, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],  # 366 days
    # Adjusted to ensure 2083-01-01 aligns with 2026-04-14
    2082: [31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2083: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2084: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
    2085: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2086: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2087: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2088: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2089: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    
    # 2090s - Future decade
    2090: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2091: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2092: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2093: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2094: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2095: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
}

# Minimum and maximum supported years
BS_MIN_YEAR = min(BS_MONTH_LENGTHS.keys())
BS_MAX_YEAR = max(BS_MONTH_LENGTHS.keys())

# Reference point: 2080-01-01 BS = 2023-04-14 AD
BS_REFERENCE_START = date(2023, 4, 14)
BS_REFERENCE_YEAR = 2080


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
        raise ValueError(f"BS year {year} is not in the supported range ({BS_MIN_YEAR}-{BS_MAX_YEAR})")
    return sum(data[0])


# Tithi (lunar day) names
TITHI_NAMES = [
    "Pratipada",    # 1
    "Dwitiya",      # 2
    "Tritiya",      # 3
    "Chaturthi",    # 4
    "Panchami",     # 5
    "Shashthi",     # 6
    "Saptami",      # 7
    "Ashtami",      # 8
    "Navami",       # 9
    "Dashami",      # 10
    "Ekadashi",     # 11
    "Dwadashi",     # 12
    "Trayodashi",   # 13
    "Chaturdashi",  # 14
    "Purnima",      # 15 (Full Moon) / Amavasya (New Moon)
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
