"""
Nepal Sambat Calendar
=====================

Nepal Sambat (नेपाल सम्वत्) is Nepal's indigenous lunar calendar,
established in 879 CE by Shankhadhar Sakhwa. It's the traditional
calendar of the Newar community and is still used for cultural
and religious purposes.

Key characteristics:
- Lunar-based calendar
- New Year falls on Kartik Shukla Pratipada (Mha Puja, during Tihar)
- Currently in the 11th century NS
- Months follow lunar phases
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Tuple, Optional

from .tithi import calculate_tithi, find_next_tithi


# Nepal Sambat epoch: 879 CE (Gregorian)
# NS 1 started on October 20, 879 CE
NS_EPOCH_YEAR = 879
NS_EPOCH_DATE = date(879, 10, 20)  # Approximate

# Nepal Sambat month names (Newari)
NS_MONTH_NAMES = [
    "Kachala",      # कछला
    "Thinla",       # थिंला  
    "Pohela",       # पोहेला
    "Silla",        # सिल्ला
    "Chilla",       # चिल्ला
    "Chaulatha",    # चौलाथा
    "Bachala",      # बाछला
    "Tachala",      # ताछला
    "Dilla",        # दिल्ला
    "Gunla",        # गुंला
    "Yanlaa",       # ञला
    "Kaulaa",       # कौला
]

NS_MONTH_NAMES_NEPALI = [
    "कछला", "थिंला", "पोहेला", "सिल्ला",
    "चिल्ला", "चौलाथा", "बाछला", "ताछला",
    "दिल्ला", "गुंला", "ञला", "कौला"
]


def gregorian_year_to_ns(gregorian_year: int) -> int:
    """
    Convert a Gregorian year to approximate Nepal Sambat year.
    
    The NS new year falls in October-November, so:
    - Before NS new year: NS = Gregorian - 879
    - After NS new year: NS = Gregorian - 878
    
    Args:
        gregorian_year: The Gregorian year
        
    Returns:
        Approximate Nepal Sambat year
        
    Example:
        >>> gregorian_year_to_ns(2026)
        1147  # or 1146 depending on month
    """
    # NS new year is approximately in October-November
    # For simplicity, we use the year that covers most of the Gregorian year
    return gregorian_year - 879 + 1


def ns_year_to_gregorian(ns_year: int) -> int:
    """
    Convert Nepal Sambat year to approximate Gregorian year.
    
    Args:
        ns_year: The Nepal Sambat year
        
    Returns:
        The Gregorian year when NS new year falls
        
    Example:
        >>> ns_year_to_gregorian(1147)
        2026
    """
    return ns_year + 879 - 1


def get_ns_new_year_date(gregorian_year: int) -> date:
    """
    Get the Gregorian date of Nepal Sambat New Year for a given year.
    
    NS New Year is Mha Puja, which falls on Kartik Amavasya 
    (the new moon of Kartik, during Tihar).
    
    Args:
        gregorian_year: The Gregorian year to find NS new year in
        
    Returns:
        The date of NS new year
        
    Example:
        >>> get_ns_new_year_date(2026)
        date(2026, 11, 8)  # Mha Puja 2026
    """
    # NS New Year is on Kartik Amavasya (new moon)
    # This is the same as Mha Puja / Laxmi Puja day
    # We search for the new moon (amavasya) in October-November
    
    # Start search from October 15 with timezone-aware datetime
    from datetime import datetime, timezone
    search_start = datetime(gregorian_year, 10, 15, 12, 0, tzinfo=timezone.utc)
    
    # find_next_tithi signature: (target_tithi, target_paksha, after=None, within_days=60)
    ns_new_year = find_next_tithi(15, "krishna", search_start, within_days=45)
    
    if ns_new_year is None:
        # Fallback to approximate date
        return date(gregorian_year, 11, 8)
    
    return ns_new_year.date()


def is_ns_new_year(check_date: date) -> bool:
    """
    Check if a given date is Nepal Sambat New Year (Mha Puja).
    
    Args:
        check_date: The date to check
        
    Returns:
        True if this is NS New Year
        
    Example:
        >>> is_ns_new_year(date(2026, 11, 8))
        True
    """
    try:
        ns_new_year = get_ns_new_year_date(check_date.year)
        return check_date == ns_new_year
    except Exception:
        return False


def get_ns_month_name(month: int, nepali: bool = False) -> str:
    """
    Get the name of a Nepal Sambat month.
    
    Args:
        month: Month number (1-12)
        nepali: If True, return Nepali/Newari name
        
    Returns:
        Month name
        
    Example:
        >>> get_ns_month_name(1)
        "Kachala"
        >>> get_ns_month_name(10, nepali=True)
        "गुंला"
    """
    if not 1 <= month <= 12:
        raise ValueError(f"Month must be 1-12, got {month}")
    
    if nepali:
        return NS_MONTH_NAMES_NEPALI[month - 1]
    return NS_MONTH_NAMES[month - 1]


def get_current_ns_year(on_date: Optional[date] = None) -> int:
    """
    Get the current Nepal Sambat year for a given date.
    
    NS New Year (Mha Puja) falls in October-November. So:
    - Dates from NS new year (Oct/Nov) to Dec 31 are in NS year = Gregorian - 878
    - Dates from Jan 1 to before NS new year are in NS year = Gregorian - 879
    
    Args:
        on_date: The date to check (default: today)
        
    Returns:
        The Nepal Sambat year
        
    Example:
        >>> get_current_ns_year(date(2026, 11, 15))
        1147  # After NS new year 2026
        >>> get_current_ns_year(date(2026, 2, 15))
        1146  # Before NS new year 2026, so previous NS year
    """
    if on_date is None:
        on_date = date.today()
    
    gregorian_year = on_date.year
    
    try:
        # Get NS new year date for THIS gregorian year
        ns_new_year_this_year = get_ns_new_year_date(gregorian_year)
        
        if on_date >= ns_new_year_this_year:
            # On or after NS new year of this Gregorian year
            # We're in the new NS year
            return gregorian_year - 879
        else:
            # Before NS new year of this Gregorian year
            # We're still in the previous NS year
            return gregorian_year - 880
    except Exception:
        # Fallback: assume before NS new year
        return gregorian_year - 880


def format_ns_date(gregorian_date: date) -> str:
    """
    Format a date in Nepal Sambat style.
    
    Note: This is an approximation. Full NS date calculation 
    requires detailed lunar calendar data which is beyond the
    scope of this implementation.
    
    Args:
        gregorian_date: The Gregorian date
        
    Returns:
        Formatted NS date string
        
    Example:
        >>> format_ns_date(date(2026, 11, 15))
        "NS 1147"
    """
    ns_year = get_current_ns_year(gregorian_date)
    return f"NS {ns_year}"


# Convenience exports
__all__ = [
    "gregorian_year_to_ns",
    "ns_year_to_gregorian",
    "get_ns_new_year_date",
    "is_ns_new_year",
    "get_ns_month_name",
    "get_current_ns_year",
    "format_ns_date",
    "NS_MONTH_NAMES",
    "NS_MONTH_NAMES_NEPALI",
]
