"""
Adhik Maas (Intercalary Month) Detection for Project Parva v2.0

Adhik Maas (also called Mal Maas or Purushottam Maas) is an extra month
inserted in the Hindu/Nepali lunar calendar to keep it synchronized with
the solar calendar.

The lunar year is ~354 days (12 months × 29.5 days), while the solar year
is ~365.25 days. This difference of ~11 days per year is reconciled by
adding an intercalary month approximately every 32-33 months.

# How Adhik Maas Works:
1. A lunar month is named after the solar month (rashi) in which the 
   full moon (Purnima) occurs.
2. If TWO lunar months have their Purnima in the SAME solar month 
   (i.e., no Sankranti occurs during the lunar month), the FIRST one 
   is Adhik Maas.
3. Adhik Maas takes the name of the following month with "Adhik" prefix.
   For example: Adhik Ashwin, Adhik Shrawan, etc.

# Why It Matters:
- Adhik Maas is considered inauspicious for certain activities
- Festivals are NOT celebrated during Adhik Maas
- Dashain in Adhik Ashwin would be celebrated in Nija (regular) Ashwin
"""

from datetime import datetime, date, timedelta, timezone
from typing import Optional, List, Dict, Any, Tuple

from .ephemeris.swiss_eph import get_sun_longitude, EphemerisError
from .ephemeris.time_utils import to_nepal_time, NEPAL_TZ
from .tithi.tithi_boundaries import find_next_tithi, find_tithi_end
from .tithi.tithi_core import calculate_tithi
from .sankranti import (
    get_sun_rashi_at_time,
    find_next_sankranti,
    BS_MONTH_NAMES,
    RASHI_NAMES,
)


# =============================================================================
# ADHIK MAAS DETECTION
# =============================================================================

def find_purnima(after: datetime, max_days: int = 35) -> Optional[datetime]:
    """
    Find the exact Purnima (full moon) moment after a given time.
    
    Purnima is the astronomical instant when the Moon-Sun elongation 
    reaches exactly 180° - this is the END of Shukla 15 tithi.
    
    Args:
        after: Search after this datetime
        max_days: Maximum days to search
    
    Returns:
        Datetime of exact Purnima moment (elongation = 180°), or None
    """
    # First find when Shukla 15 starts
    shukla_15_start = find_next_tithi(15, "shukla", after, within_days=max_days)
    
    if shukla_15_start is None:
        return None
    
    # The ACTUAL Purnima moment is when Shukla 15 ENDS (elongation = 180°)
    purnima_moment = find_tithi_end(shukla_15_start)
    
    return purnima_moment


def find_amavasya(after: datetime, max_days: int = 35) -> Optional[datetime]:
    """
    Find the exact Amavasya (new moon) moment after a given time.
    
    Amavasya is the astronomical instant when the Moon-Sun elongation
    reaches exactly 360° (0°) - this is the END of Krishna 15 tithi.
    
    Args:
        after: Search after this datetime
        max_days: Maximum days to search
    
    Returns:
        Datetime of exact Amavasya moment (elongation = 0°/360°), or None
    """
    # First find when Krishna 15 starts
    krishna_15_start = find_next_tithi(15, "krishna", after, within_days=max_days)
    
    if krishna_15_start is None:
        return None
    
    # The ACTUAL Amavasya moment is when Krishna 15 ENDS (elongation = 360°)
    amavasya_moment = find_tithi_end(krishna_15_start)
    
    return amavasya_moment


def get_lunar_month_boundaries(after: datetime) -> Tuple[datetime, datetime, datetime]:
    """
    Get the boundaries of the lunar month starting after the given time.
    
    A lunar month runs from Amavasya (new moon) to Amavasya.
    
    Args:
        after: Search after this datetime
    
    Returns:
        Tuple of (start_amavasya, purnima, end_amavasya)
    """
    start = find_amavasya(after)
    if start is None:
        raise EphemerisError(f"Could not find Amavasya after {after}")
    
    purnima = find_purnima(start, max_days=20)
    if purnima is None:
        raise EphemerisError(f"Could not find Purnima after {start}")
    
    end = find_amavasya(purnima, max_days=20)
    if end is None:
        raise EphemerisError(f"Could not find ending Amavasya after {purnima}")
    
    return (start, purnima, end)


def is_adhik_maas(
    lunar_month_start: datetime,
    lunar_month_end: datetime
) -> bool:
    """
    Check if a lunar month is an Adhik Maas (intercalary month).
    
    A lunar month is Adhik if NO sankranti (solar transit) occurs during it.
    This means the Sun stays in the same rashi for the entire lunar month.
    
    Args:
        lunar_month_start: Start of lunar month (Amavasya)
        lunar_month_end: End of lunar month (next Amavasya)
    
    Returns:
        True if this is Adhik Maas
    """
    # Get Sun's rashi at start and end of lunar month
    start_rashi = get_sun_rashi_at_time(lunar_month_start)
    end_rashi = get_sun_rashi_at_time(lunar_month_end)
    
    # If same rashi, no sankranti occurred = Adhik Maas
    return start_rashi == end_rashi


def get_lunar_month_name(purnima_time: datetime) -> str:
    """
    Get the name of a lunar month based on when Purnima occurs.
    
    NOTE: This uses a SOLAR-BASED naming convention (simplified):
    The lunar month is named after the solar month (Sun's rashi) in which
    the full moon (Purnima) falls.
    
    Traditional naming uses the Moon's nakshatra at Purnima, which gives
    names like Kartika (Krittika nakshatra), Margashirsha (Mrigashira), etc.
    This implementation uses the solar mapping for simplicity and 
    consistency with the BS solar calendar.
    
    Args:
        purnima_time: Datetime of Purnima (full moon moment, elongation=180°)
    
    Returns:
        Lunar month name (BS month name, solar-based)
    """
    rashi = get_sun_rashi_at_time(purnima_time)
    return BS_MONTH_NAMES[rashi]


def analyze_lunar_month(after: datetime) -> Dict[str, Any]:
    """
    Analyze the next lunar month after a given time.
    
    Args:
        after: Search after this datetime
    
    Returns:
        Dict with lunar month analysis including is_adhik flag
    """
    start, purnima, end = get_lunar_month_boundaries(after)
    
    is_adhik = is_adhik_maas(start, end)
    month_name = get_lunar_month_name(purnima)
    
    start_rashi = get_sun_rashi_at_time(start)
    end_rashi = get_sun_rashi_at_time(end)
    
    return {
        "start": start,
        "purnima": purnima,
        "end": end,
        "duration_days": (end - start).days,
        "month_name": month_name,
        "is_adhik": is_adhik,
        "display_name": f"Adhik {month_name}" if is_adhik else month_name,
        "start_rashi": RASHI_NAMES[start_rashi],
        "end_rashi": RASHI_NAMES[end_rashi],
        "sankranti_in_month": start_rashi != end_rashi,
    }


def find_adhik_maas_in_range(
    start_date: date,
    end_date: date
) -> List[Dict[str, Any]]:
    """
    Find all Adhik Maas occurrences in a date range.
    
    Args:
        start_date: Start of search range
        end_date: End of search range
    
    Returns:
        List of Adhik Maas info dicts
    """
    results = []
    
    current = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    end = datetime.combine(end_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    
    while current < end:
        try:
            analysis = analyze_lunar_month(current)
            
            if analysis["is_adhik"]:
                results.append({
                    "year": to_nepal_time(analysis["start"]).year,
                    "month_name": analysis["display_name"],
                    "start_date": to_nepal_time(analysis["start"]).date(),
                    "end_date": to_nepal_time(analysis["end"]).date(),
                    "purnima_date": to_nepal_time(analysis["purnima"]).date(),
                })
            
            # Move to after this lunar month ends
            current = analysis["end"] + timedelta(days=1)
            
        except EphemerisError:
            # Skip errors and continue
            current += timedelta(days=30)
    
    return results


def find_adhik_maas_years(start_year: int, end_year: int) -> List[Dict[str, Any]]:
    """
    Find Adhik Maas occurrences for a range of years.
    
    Args:
        start_year: Start Gregorian year
        end_year: End Gregorian year (inclusive)
    
    Returns:
        List of Adhik Maas info for each occurrence
    """
    start = date(start_year, 1, 1)
    end = date(end_year + 1, 1, 1)
    return find_adhik_maas_in_range(start, end)


# =============================================================================
# NIJA MAAS DETECTION
# =============================================================================

def is_nija_maas(after: datetime) -> bool:
    """
    Check if the lunar month is Nija (regular/pure) as opposed to Adhik.
    
    Nija Maas has a sankranti during it (Sun changes rashi).
    
    Args:
        after: Time to check from
    
    Returns:
        True if the lunar month is Nija (not Adhik)
    """
    analysis = analyze_lunar_month(after)
    return not analysis["is_adhik"]


# =============================================================================
# FESTIVAL ADJUSTMENTS FOR ADHIK MAAS
# =============================================================================

def should_celebrate_festival(
    festival_date: datetime,
    festival_bs_month: int
) -> Tuple[bool, str]:
    """
    Check if a festival should be celebrated on a given date.
    
    Festivals are NOT celebrated during Adhik Maas. They are postponed
    to the Nija (regular) month that follows.
    
    Args:
        festival_date: Proposed date for festival
        festival_bs_month: Expected BS month for the festival (1-12)
    
    Returns:
        Tuple of (should_celebrate, reason)
    """
    # Find the lunar month containing this date
    # We search from 30 days before to find the start
    search_start = festival_date - timedelta(days=30)
    
    try:
        analysis = analyze_lunar_month(search_start)
        
        # Check if festival_date falls within this lunar month
        if analysis["start"] <= festival_date <= analysis["end"]:
            if analysis["is_adhik"]:
                return (False, f"Date falls in {analysis['display_name']} - wait for Nija")
            else:
                return (True, "Date is in regular (Nija) month")
        
        # Festival might be in next lunar month
        next_analysis = analyze_lunar_month(analysis["end"])
        
        if next_analysis["start"] <= festival_date <= next_analysis["end"]:
            if next_analysis["is_adhik"]:
                return (False, f"Date falls in {next_analysis['display_name']} - wait for Nija")
            else:
                return (True, "Date is in regular (Nija) month")
        
        return (True, "Unable to determine lunar month - assuming Nija")
        
    except EphemerisError as e:
        return (True, f"Calculation error, assuming Nija: {e}")
