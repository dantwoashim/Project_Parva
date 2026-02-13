"""
Tithi (Lunar Day) Calculator
============================

This module calculates the tithi (lunar day) for any given date.
Tithis are fundamental to Nepali festival date calculation, as most
festivals fall on specific tithis rather than fixed calendar dates.

A tithi is approximately 1/30th of a lunar month. There are 30 tithis
in a lunar month:
- Tithis 1-15 in Shukla Paksha (bright/waxing fortnight)
- Tithis 1-15 in Krishna Paksha (dark/waning fortnight)

The 15th tithi of Shukla is Purnima (full moon).
The 15th tithi of Krishna is Amavasya (new moon).

Usage:
    >>> from app.calendar.tithi import calculate_tithi, find_next_tithi
    
    >>> tithi, paksha = calculate_tithi(date(2026, 9, 15))
    >>> print(f"Tithi: {tithi}, Paksha: {paksha}")
    
    >>> dashain_start = find_next_tithi(1, "shukla", date(2026, 9, 1), month=6)
"""

from __future__ import annotations

from datetime import date, timedelta
import math
from typing import Literal, Optional, Tuple

from .constants import (
    SYNODIC_MONTH,
    KNOWN_NEW_MOON,
    TITHI_NAMES,
    TITHI_NAMES_NEPALI,
    PAKSHA_SHUKLA,
    PAKSHA_KRISHNA,
)


PakshaType = Literal["shukla", "krishna"]


def calculate_moon_phase(target_date: date) -> float:
    """
    Calculate the moon phase on a given date.
    
    Uses a simplified astronomical calculation based on the synodic month.
    
    Args:
        target_date: The date to calculate for
    
    Returns:
        Moon phase as a fraction (0.0 = new moon, 0.5 = full moon, 1.0 = next new moon)
    
    Examples:
        >>> phase = calculate_moon_phase(date(2023, 1, 21))  # Known new moon
        >>> abs(phase) < 0.05  # Should be close to 0
        True
    """
    # Days since known new moon
    days_since = (target_date - KNOWN_NEW_MOON).days
    
    # Calculate phase (0-1)
    phase = (days_since % SYNODIC_MONTH) / SYNODIC_MONTH
    
    return phase


def calculate_tithi(target_date: date) -> tuple[int, PakshaType]:
    """
    Calculate the tithi (lunar day) for a given date.
    
    This uses astronomical moon phase calculation to determine the tithi.
    The calculation is based on the angular distance between sun and moon.
    
    Args:
        target_date: The date to calculate tithi for
    
    Returns:
        Tuple of (tithi number 1-15, paksha "shukla" or "krishna")
    
    Notes:
        - Shukla Paksha: Waxing moon (new moon → full moon), tithis 1-15
        - Krishna Paksha: Waning moon (full moon → new moon), tithis 1-15
        - Accuracy is typically within ±1 day for festival calculations
    
    Examples:
        >>> tithi, paksha = calculate_tithi(date(2023, 1, 21))  # New moon day
        >>> tithi == 15 or tithi == 1  # Around new moon
        True
        >>> paksha in ("shukla", "krishna")
        True
    """
    phase = calculate_moon_phase(target_date)
    
    # Convert phase to tithi (0-30)
    # 0 = new moon = end of Krishna Amavasya / start of Shukla Pratipada
    # 0.5 = full moon = end of Shukla Purnima / start of Krishna Pratipada
    tithi_raw = phase * 30
    
    if tithi_raw < 15:
        # Shukla Paksha (waxing)
        tithi = int(tithi_raw) + 1  # 1-15
        paksha = PAKSHA_SHUKLA
    else:
        # Krishna Paksha (waning)
        tithi = int(tithi_raw - 15) + 1  # 1-15
        paksha = PAKSHA_KRISHNA
    
    # Handle edge case where tithi becomes 16
    if tithi > 15:
        tithi = 15
    
    return (tithi, paksha)


def get_paksha(target_date: date) -> PakshaType:
    """
    Get just the paksha (lunar fortnight) for a date.
    
    Args:
        target_date: The date to check
    
    Returns:
        "shukla" for waxing moon (bright fortnight)
        "krishna" for waning moon (dark fortnight)
    
    Examples:
        >>> get_paksha(date(2023, 1, 21))  # New moon - start of shukla
        'shukla'
    """
    _, paksha = calculate_tithi(target_date)
    return paksha


def get_tithi_name(tithi: int, language: str = "english") -> str:
    """
    Get the name of a tithi.
    
    Args:
        tithi: Tithi number (1-15)
        language: "english" or "nepali"
    
    Returns:
        Name of the tithi
    
    Raises:
        ValueError: If tithi is not 1-15
    
    Examples:
        >>> get_tithi_name(1)
        'Pratipada'
        >>> get_tithi_name(8, "nepali")
        'अष्टमी'
    """
    if tithi < 1 or tithi > 15:
        raise ValueError(f"Invalid tithi: {tithi}. Must be 1-15.")
    
    if language == "nepali":
        return TITHI_NAMES_NEPALI[tithi - 1]
    return TITHI_NAMES[tithi - 1]


def find_next_tithi(
    tithi: int,
    paksha: PakshaType,
    after_date: date,
    bs_month: int | None = None,
    max_search_days: int = 60,
) -> date | None:
    """
    Find the next occurrence of a specific tithi.
    
    This is the core function for festival date calculation. Most Nepali
    festivals fall on specific tithis in specific months.
    
    Args:
        tithi: The tithi number to find (1-15)
        paksha: Which paksha ("shukla" or "krishna")
        after_date: Search starting from this date
        bs_month: Optional - restrict to occurrences in this BS month (1-12)
        max_search_days: Maximum days to search forward
    
    Returns:
        Date of next occurrence, or None if not found in range
    
    Examples:
        >>> # Find next Shukla Pratipada (start of Dashain 2026)
        >>> next_date = find_next_tithi(1, "shukla", date(2026, 9, 1))
        
        >>> # Find next Purnima (full moon)
        >>> full_moon = find_next_tithi(15, "shukla", date(2026, 1, 1))
    """
    if tithi < 1 or tithi > 15:
        raise ValueError(f"Invalid tithi: {tithi}. Must be 1-15.")
    
    if paksha not in (PAKSHA_SHUKLA, PAKSHA_KRISHNA):
        raise ValueError(f"Invalid paksha: {paksha}. Must be 'shukla' or 'krishna'.")
    
    # Import here to avoid circular imports
    from .bikram_sambat import gregorian_to_bs
    
    current_date = after_date
    
    for _ in range(max_search_days):
        current_date += timedelta(days=1)
        
        calc_tithi, calc_paksha = calculate_tithi(current_date)
        
        # Check if this is our target tithi
        if calc_tithi == tithi and calc_paksha == paksha:
            # If month restriction, check BS month
            if bs_month is not None:
                try:
                    _, current_bs_month, _ = gregorian_to_bs(current_date)
                    if current_bs_month != bs_month:
                        continue
                except ValueError:
                    # Date outside our BS range, skip
                    continue
            
            return current_date
    
    return None


def find_purnima(after_date: date, bs_month: int | None = None) -> date | None:
    """
    Find the next Purnima (full moon).
    
    Convenience function as many festivals fall on Purnima.
    
    Args:
        after_date: Search starting from this date
        bs_month: Optional - restrict to this BS month
    
    Returns:
        Date of next Purnima
    
    Examples:
        >>> # Find next Purnima after today
        >>> purnima = find_purnima(date.today())
        
        >>> # Find Falgun Purnima (Holi)
        >>> holi = find_purnima(date(2026, 1, 1), bs_month=11)
    """
    return find_next_tithi(15, PAKSHA_SHUKLA, after_date, bs_month)


def find_amavasya(after_date: date, bs_month: int | None = None) -> date | None:
    """
    Find the next Amavasya (new moon).
    
    Convenience function for new moon based observances.
    
    Args:
        after_date: Search starting from this date
        bs_month: Optional - restrict to this BS month
    
    Returns:
        Date of next Amavasya
    """
    return find_next_tithi(15, PAKSHA_KRISHNA, after_date, bs_month)


def get_moon_phase_name(target_date: date) -> str:
    """
    Get a human-readable description of the moon phase.
    
    Args:
        target_date: The date to describe
    
    Returns:
        Description like "Waxing Crescent", "Full Moon", etc.
    
    Examples:
        >>> get_moon_phase_name(date(2023, 1, 21))  # New moon
        'New Moon'
    """
    phase = calculate_moon_phase(target_date)
    
    # Define phase ranges
    if phase < 0.033 or phase > 0.967:
        return "New Moon"
    elif phase < 0.233:
        return "Waxing Crescent"
    elif phase < 0.283:
        return "First Quarter"
    elif phase < 0.467:
        return "Waxing Gibbous"
    elif phase < 0.533:
        return "Full Moon"
    elif phase < 0.717:
        return "Waning Gibbous"
    elif phase < 0.767:
        return "Last Quarter"
    else:
        return "Waning Crescent"


def days_until_next_purnima(from_date: date | None = None) -> int:
    """
    Calculate days until the next full moon.
    
    Args:
        from_date: Starting date (defaults to today)
    
    Returns:
        Number of days until next Purnima
    """
    if from_date is None:
        from_date = date.today()
    
    next_purnima = find_purnima(from_date)
    if next_purnima is None:
        return -1
    
    return (next_purnima - from_date).days


def is_auspicious_tithi(tithi: int) -> bool:
    """
    Check if a tithi is traditionally considered auspicious.
    
    Certain tithis are considered more auspicious for ceremonies
    and festivals in Nepali/Hindu tradition.
    
    Args:
        tithi: Tithi number (1-15)
    
    Returns:
        True if considered auspicious
    """
    # Generally auspicious tithis
    auspicious = {2, 3, 5, 7, 10, 11, 12, 13, 15}
    
    # Avoid: Rikta tithis (4, 9, 14) and Amavasya (15 Krishna) for most purposes
    return tithi in auspicious
