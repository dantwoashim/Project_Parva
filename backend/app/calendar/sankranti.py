"""
Sankranti (Solar Transit) Detection for Project Parva v2.0

Sankranti is the moment when the Sun enters a new zodiac sign (rashi).
This is critical for:
1. Bikram Sambat month boundaries (solar calendar)
2. Major festivals (Maghe Sankranti, Mesh Sankranti/BS New Year)
3. Adhik Maas (intercalary month) detection

The 12 sankrantis mark the 12 BS months:
- Mesh Sankranti → Baishakh (April)
- Vrishabha Sankranti → Jestha (May)
- Mithuna Sankranti → Ashadh (June)
- Karka Sankranti → Shrawan (July)
- Simha Sankranti → Bhadra (August)
- Kanya Sankranti → Ashwin (September)
- Tula Sankranti → Kartik (October)
- Vrishchika Sankranti → Mangsir (November)
- Dhanu Sankranti → Poush (December)
- Makara Sankranti → Magh (January) ← Major festival
- Kumbha Sankranti → Falgun (February)
- Meena Sankranti → Chaitra (March)
"""

from datetime import datetime, date, timedelta, timezone
from typing import Tuple, Optional, List, Dict, Any

from .ephemeris.swiss_eph import (
    get_sun_longitude,
    get_julian_day,
    julian_day_to_datetime,
    EphemerisError,
)
from .ephemeris.time_utils import (
    to_nepal_time,
    NEPAL_TZ,
)


# =============================================================================
# CONSTANTS
# =============================================================================

# Rashi (zodiac sign) names in order
RASHI_NAMES = [
    "Mesha",     # Aries - 0°
    "Vrishabha", # Taurus - 30°
    "Mithuna",   # Gemini - 60°
    "Karka",     # Cancer - 90°
    "Simha",     # Leo - 120°
    "Kanya",     # Virgo - 150°
    "Tula",      # Libra - 180°
    "Vrishchika",# Scorpio - 210°
    "Dhanu",     # Sagittarius - 240°
    "Makara",    # Capricorn - 270°
    "Kumbha",    # Aquarius - 300°
    "Meena",     # Pisces - 330°
]

# BS month names corresponding to each rashi
BS_MONTH_NAMES = [
    "Baishakh",  # Mesha
    "Jestha",    # Vrishabha
    "Ashadh",    # Mithuna
    "Shrawan",   # Karka
    "Bhadra",    # Simha
    "Ashwin",    # Kanya
    "Kartik",    # Tula
    "Mangsir",   # Vrishchika
    "Poush",     # Dhanu
    "Magh",      # Makara
    "Falgun",    # Kumbha
    "Chaitra",   # Meena
]

# Rashi boundary degrees
RASHI_DEGREES = [i * 30 for i in range(12)]  # [0, 30, 60, ..., 330]


# =============================================================================
# SANKRANTI DETECTION
# =============================================================================

def _angular_error(value_deg: float, target_deg: float) -> float:
    """
    Signed angular difference in range [-180, 180).
    """
    return ((value_deg - target_deg + 180.0) % 360.0) - 180.0


def _bisect_sankranti(target_degree: float, low: datetime, high: datetime, tolerance_seconds: int = 60) -> datetime:
    """
    Monotonic bisection fallback for sankranti root-finding.
    """
    tolerance = timedelta(seconds=tolerance_seconds)
    for _ in range(60):
        if high - low < tolerance:
            break
        mid = low + (high - low) / 2
        mid_err = _angular_error(get_sun_longitude(mid, sidereal=True), target_degree)
        low_err = _angular_error(get_sun_longitude(low, sidereal=True), target_degree)
        if low_err == 0:
            return low
        if mid_err == 0:
            return mid
        if low_err * mid_err <= 0:
            high = mid
        else:
            low = mid
    return high


def find_sankranti_brent(
    target_degree: float,
    low: datetime,
    high: datetime,
    tolerance_seconds: int = 60,
    max_iterations: int = 50,
) -> datetime:
    """
    Brent-style hybrid root finder for Sun longitude transit.

    Returns the UTC datetime where Sun longitude crosses `target_degree`.
    Falls back to robust bisection if a valid sign bracket is not found.
    """
    tol = float(tolerance_seconds)

    a = low.timestamp()
    b = high.timestamp()

    def f(ts: float) -> float:
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        return _angular_error(get_sun_longitude(dt, sidereal=True), target_degree)

    fa = f(a)
    fb = f(b)
    if fa == 0:
        return datetime.fromtimestamp(a, tz=timezone.utc)
    if fb == 0:
        return datetime.fromtimestamp(b, tz=timezone.utc)
    if fa * fb > 0:
        return _bisect_sankranti(target_degree, low, high, tolerance_seconds=tolerance_seconds)

    if abs(fa) < abs(fb):
        a, b = b, a
        fa, fb = fb, fa

    c = a
    fc = fa
    d = a
    mflag = True

    for _ in range(max_iterations):
        if abs(b - a) <= tol or fb == 0:
            return datetime.fromtimestamp(b, tz=timezone.utc)

        if fa != fc and fb != fc:
            # Inverse quadratic interpolation
            s = (
                (a * fb * fc) / ((fa - fb) * (fa - fc))
                + (b * fa * fc) / ((fb - fa) * (fb - fc))
                + (c * fa * fb) / ((fc - fa) * (fc - fb))
            )
        else:
            # Secant
            s = b - fb * (b - a) / (fb - fa)

        cond1 = not (min((3 * a + b) / 4, b) < s < max((3 * a + b) / 4, b))
        cond2 = mflag and abs(s - b) >= abs(b - c) / 2
        cond3 = (not mflag) and abs(s - b) >= abs(c - d) / 2
        cond4 = mflag and abs(b - c) < tol
        cond5 = (not mflag) and abs(c - d) < tol

        if cond1 or cond2 or cond3 or cond4 or cond5:
            s = (a + b) / 2
            mflag = True
        else:
            mflag = False

        fs = f(s)
        d, c = c, b
        fc = fb

        if fa * fs < 0:
            b = s
            fb = fs
        else:
            a = s
            fa = fs

        if abs(fa) < abs(fb):
            a, b = b, a
            fa, fb = fb, fa

    return datetime.fromtimestamp(b, tz=timezone.utc)

def get_sun_rashi_at_time(dt: datetime) -> int:
    """
    Get the rashi (0-11) the Sun is currently in.
    
    Args:
        dt: Datetime with timezone
    
    Returns:
        Rashi index 0-11 (0=Mesha, 11=Meena)
    """
    sun_long = get_sun_longitude(dt, sidereal=True)
    return int(sun_long / 30) % 12


def find_sankranti(
    target_rashi: int,
    after: datetime,
    max_days: int = 40
) -> Optional[datetime]:
    """
    Find when the Sun enters a specific rashi (sankranti moment).
    
    Uses binary search to find the exact transition time. If `after` is
    already inside the target rashi, searches backward to find the entry.
    
    Args:
        target_rashi: Rashi index 0-11 to find entry for
        after: Search after this datetime
        max_days: Maximum days to search forward (or backward if in target)
    
    Returns:
        Datetime of sankranti (Sun entering target rashi), or None
    
    Example:
        >>> find_sankranti(9, datetime(2026, 1, 1, tzinfo=timezone.utc))
        datetime(2026, 1, 14, 8, 30, tzinfo=timezone.utc)  # Makara Sankranti
    """
    target_degree = target_rashi * 30  # Entry degree for rashi
    prev_rashi = (target_rashi - 1) % 12  # Rashi before target
    
    # Check current position
    current_rashi = get_sun_rashi_at_time(after)
    
    # CASE 1: Already in target rashi - search backward to find entry
    if current_rashi == target_rashi:
        # Search backward to find when we were in prev_rashi
        step = timedelta(days=1)
        search_point = after
        
        for _ in range(max_days):
            search_point -= step
            rashi = get_sun_rashi_at_time(search_point)
            if rashi == prev_rashi:
                # Found a point before the crossing
                low = search_point
                high = after
                break
        else:
            # Couldn't find previous rashi, can't determine crossing
            return None
    
    # CASE 2: In prev_rashi - crossing is ahead
    elif current_rashi == prev_rashi:
        low = after
        # Search forward to find when we enter target
        step = timedelta(days=1)
        search_point = after
        
        for _ in range(max_days):
            search_point += step
            rashi = get_sun_rashi_at_time(search_point)
            if rashi == target_rashi:
                high = search_point
                break
        else:
            return None
    
    # CASE 3: Neither - search forward until we find the window
    else:
        step = timedelta(days=1)
        search_point = after
        found_prev = None
        found_target = None
        
        for _ in range(max_days * 12):  # May need to wait for full cycle
            search_point += step
            rashi = get_sun_rashi_at_time(search_point)
            
            if rashi == prev_rashi:
                found_prev = search_point
            elif rashi == target_rashi and found_prev is not None:
                found_target = search_point
                break
        
        if found_target is None:
            return None
        
        low = found_prev
        high = found_target
    
    return find_sankranti_brent(target_degree, low, high, tolerance_seconds=60)


def find_next_sankranti(after: datetime) -> Tuple[int, str, datetime]:
    """
    Find the next sankranti (any rashi) after the given time.
    
    Args:
        after: Search after this datetime
    
    Returns:
        Tuple of (rashi_index, rashi_name, sankranti_datetime)
    """
    current_rashi = get_sun_rashi_at_time(after)
    next_rashi = (current_rashi + 1) % 12
    
    sankranti_time = find_sankranti(next_rashi, after)
    
    if sankranti_time is None:
        raise EphemerisError(f"Could not find next sankranti after {after}")
    
    return (next_rashi, RASHI_NAMES[next_rashi], sankranti_time)


def get_sankrantis_in_year(year: int) -> List[Dict[str, Any]]:
    """
    Get all 12 sankrantis for a Gregorian year.
    
    Args:
        year: Gregorian year
    
    Returns:
        List of sankranti info dicts with rashi, name, bs_month, datetime
    """
    results = []
    
    # Start from beginning of year
    current = datetime(year, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    end = datetime(year + 1, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    
    while current < end:
        rashi_idx, rashi_name, sankranti_dt = find_next_sankranti(current)
        
        if sankranti_dt >= end:
            break
        
        results.append({
            "rashi_index": rashi_idx,
            "rashi_name": rashi_name,
            "bs_month": BS_MONTH_NAMES[rashi_idx],
            "bs_month_number": rashi_idx + 1,
            "datetime_utc": sankranti_dt,
            "datetime_nepal": to_nepal_time(sankranti_dt),
            "date": to_nepal_time(sankranti_dt).date(),
        })
        
        # Move past this sankranti
        current = sankranti_dt + timedelta(days=1)
    
    return results


# =============================================================================
# SPECIFIC SANKRANTI FINDERS
# =============================================================================

def find_mesh_sankranti(year: int) -> datetime:
    """
    Find Mesh Sankranti (BS New Year) for a given year.
    
    Mesh Sankranti is when Sun enters Mesha (Aries) rashi,
    marking the first day of Baishakh and the BS New Year.
    
    Usually falls around April 13-14.
    
    Args:
        year: Gregorian year
    
    Returns:
        Datetime of Mesh Sankranti
    """
    # Search around mid-April
    search_start = datetime(year, 4, 1, 0, 0, 0, tzinfo=timezone.utc)
    return find_sankranti(0, search_start, max_days=30)


def find_makara_sankranti(year: int) -> datetime:
    """
    Find Makara Sankranti for a given year.
    
    Makara Sankranti is when Sun enters Makara (Capricorn) rashi.
    This is a major festival, usually on January 14-15.
    Marks the first day of Magh month.
    
    Args:
        year: Gregorian year
    
    Returns:
        Datetime of Makara Sankranti
    """
    # Search around mid-January
    search_start = datetime(year, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    return find_sankranti(9, search_start, max_days=30)


# =============================================================================
# BS MONTH BOUNDARIES
# =============================================================================

def get_bs_month_start(bs_year: int, bs_month: int) -> date:
    """
    Get the Gregorian date when a BS month starts.
    
    The BS month starts when the Sun enters the corresponding rashi.
    
    Args:
        bs_year: Bikram Sambat year
        bs_month: BS month 1-12 (1=Baishakh)
    
    Returns:
        Gregorian date of month start
    """
    # Convert BS year to approximate Gregorian year
    # BS year starts in April, so:
    # - Baishakh (month 1) to Poush (month 9): same year + 57
    # - Magh to Chaitra (months 10-12): next year + 56
    
    if bs_month <= 9:
        greg_year = bs_year - 57
    else:
        greg_year = bs_year - 56
    
    # Target rashi is month - 1 (0-indexed)
    target_rashi = bs_month - 1
    
    # Approximate search start based on month
    month_starts = [
        (4, 1),   # Baishakh ~April
        (5, 1),   # Jestha ~May
        (6, 1),   # Ashadh ~June
        (7, 1),   # Shrawan ~July
        (8, 1),   # Bhadra ~August
        (9, 1),   # Ashwin ~September
        (10, 1),  # Kartik ~October
        (11, 1),  # Mangsir ~November
        (12, 1),  # Poush ~December
        (1, 1),   # Magh ~January
        (2, 1),   # Falgun ~February
        (3, 1),   # Chaitra ~March
    ]
    
    greg_month, greg_day = month_starts[bs_month - 1]
    search_start = datetime(greg_year, greg_month, greg_day, 0, 0, 0, tzinfo=timezone.utc)
    
    sankranti = find_sankranti(target_rashi, search_start - timedelta(days=15), max_days=45)
    
    if sankranti is None:
        raise EphemerisError(f"Could not find sankranti for BS {bs_year}/{bs_month}")
    
    # Return the Nepal date
    return to_nepal_time(sankranti).date()


def get_bs_year_sankrantis(bs_year: int) -> List[Dict[str, Any]]:
    """
    Get all 12 sankrantis for a BS year.
    
    Args:
        bs_year: Bikram Sambat year
    
    Returns:
        List of sankranti info for each BS month
    """
    results = []
    
    for month in range(1, 13):
        month_start = get_bs_month_start(bs_year, month)
        results.append({
            "bs_year": bs_year,
            "bs_month": month,
            "bs_month_name": BS_MONTH_NAMES[month - 1],
            "start_date": month_start,
        })
    
    return results


# =============================================================================
# COMPUTED BS CALENDAR (for extended range)
# =============================================================================

def compute_bs_month_lengths(bs_year: int) -> List[int]:
    """
    Compute the number of days in each BS month for a given year.
    
    This uses ephemeris to calculate exact sankranti dates,
    allowing calculation for any year (not just lookup table years).
    
    Args:
        bs_year: Bikram Sambat year
    
    Returns:
        List of 12 integers, days in each month
    """
    month_lengths = []
    
    # Get start of each month and next month
    for month in range(1, 13):
        start = get_bs_month_start(bs_year, month)
        
        if month < 12:
            next_start = get_bs_month_start(bs_year, month + 1)
        else:
            # Next month is Baishakh of next year
            next_start = get_bs_month_start(bs_year + 1, 1)
        
        days = (next_start - start).days
        month_lengths.append(days)
    
    return month_lengths


def compute_bs_year_days(bs_year: int) -> int:
    """
    Compute total days in a BS year.
    
    Args:
        bs_year: Bikram Sambat year
    
    Returns:
        Total days (usually 365 or 366)
    """
    return sum(compute_bs_month_lengths(bs_year))
