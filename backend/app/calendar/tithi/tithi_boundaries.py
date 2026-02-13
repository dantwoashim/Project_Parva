"""
Tithi Boundary Finding for Project Parva v2.0

Uses Brent's method (scipy or custom implementation) to find
exact tithi transitions with high precision.

A tithi boundary occurs when elongation = n × 12° (where n = 0, 1, 2, ... 29)
"""

from datetime import datetime, date, timedelta, timezone
from typing import Optional, Tuple, List

from .tithi_core import calculate_tithi, TITHI_SPAN
from ..ephemeris.positions import get_tithi_angle
from ..ephemeris.swiss_eph import get_julian_day, julian_day_to_datetime
from ..ephemeris.time_utils import to_nepal_time


# =============================================================================
# BOUNDARY FINDING
# =============================================================================

def find_tithi_end(
    dt: datetime,
    max_iterations: int = 50,
    tolerance_seconds: int = 60
) -> datetime:
    """
    Find when the current tithi ends using binary search.
    
    Args:
        dt: Starting datetime
        max_iterations: Maximum search iterations
        tolerance_seconds: Precision in seconds
    
    Returns:
        Datetime when current tithi ends (next tithi begins)
    
    Note:
        A tithi typically lasts about 19-26 hours (mean ~23.6 hours).
    """
    # Get current tithi
    current_elongation = get_tithi_angle(dt)
    current_tithi = int(current_elongation / TITHI_SPAN)
    
    # The next tithi boundary is at (current_tithi + 1) * 12 degrees
    target_elongation = ((current_tithi + 1) * TITHI_SPAN) % 360
    
    # Binary search window
    # Search up to 30 hours ahead to safely cover slow boundaries.
    start_dt = dt
    end_dt = dt + timedelta(hours=30)
    
    tolerance = timedelta(seconds=tolerance_seconds)
    
    for _ in range(max_iterations):
        mid_dt = start_dt + (end_dt - start_dt) / 2
        mid_elongation = get_tithi_angle(mid_dt)
        mid_tithi = int(mid_elongation / TITHI_SPAN)
        
        if end_dt - start_dt < tolerance:
            return end_dt
        
        # Check if we've crossed the boundary
        if mid_tithi == current_tithi:
            # Haven't reached boundary yet
            start_dt = mid_dt
        else:
            # Crossed boundary, narrow down
            end_dt = mid_dt
    
    return end_dt


def find_tithi_start(
    dt: datetime,
    max_iterations: int = 50,
    tolerance_seconds: int = 60
) -> datetime:
    """
    Find when the current tithi started.
    
    Args:
        dt: Reference datetime
        max_iterations: Maximum search iterations
        tolerance_seconds: Precision in seconds
    
    Returns:
        Datetime when current tithi started
    """
    # Get current tithi
    current_elongation = get_tithi_angle(dt)
    current_tithi = int(current_elongation / TITHI_SPAN)
    
    # Binary search window (look back up to 30 hours)
    start_dt = dt - timedelta(hours=30)
    end_dt = dt
    
    tolerance = timedelta(seconds=tolerance_seconds)
    
    for _ in range(max_iterations):
        mid_dt = start_dt + (end_dt - start_dt) / 2
        mid_elongation = get_tithi_angle(mid_dt)
        mid_tithi = int(mid_elongation / TITHI_SPAN)
        
        if end_dt - start_dt < tolerance:
            return end_dt
        
        if mid_tithi == current_tithi:
            # Still in current tithi, go further back
            end_dt = mid_dt
        else:
            # Before current tithi, narrow forward
            start_dt = mid_dt
    
    return end_dt


def get_tithi_window(dt: datetime) -> Tuple[datetime, datetime]:
    """
    Get the start and end times of the tithi containing dt.
    
    Args:
        dt: Datetime within the tithi
    
    Returns:
        Tuple of (start_time, end_time)
    """
    start = find_tithi_start(dt)
    end = find_tithi_end(dt)
    return (start, end)


# =============================================================================
# FIND SPECIFIC TITHI
# =============================================================================

def find_next_tithi(
    target_tithi: int,
    target_paksha: str,
    after: datetime = None,
    within_days: int = 60
) -> Optional[datetime]:
    """
    Find the next occurrence of a specific tithi.
    
    Args:
        target_tithi: Tithi number 1-15
        target_paksha: "shukla" or "krishna"
        after: Search after this datetime (default: now)
        within_days: Maximum days to search
    
    Returns:
        Datetime when the target tithi begins, or None if not found
    
    Example:
        >>> find_next_tithi(10, "shukla")  # Next Dashami Shukla
        datetime(2026, 2, 12, 3, 45, 0)
    """
    if target_tithi < 1 or target_tithi > 15:
        raise ValueError("target_tithi must be in range 1..15")
    if target_paksha not in {"shukla", "krishna"}:
        raise ValueError("target_paksha must be 'shukla' or 'krishna'")

    if after is None:
        after = datetime.now(timezone.utc)
    elif isinstance(after, date) and not isinstance(after, datetime):
        after = datetime.combine(after, datetime.min.time()).replace(tzinfo=timezone.utc)
    elif isinstance(after, datetime) and after.tzinfo is None:
        after = after.replace(tzinfo=timezone.utc)
    
    # Convert target to absolute tithi (1-30)
    if target_paksha == "krishna":
        target_absolute = target_tithi + 15
    else:
        target_absolute = target_tithi
    
    # Walk forward day by day
    search_dt = after
    end_dt = after + timedelta(days=within_days)
    
    while search_dt < end_dt:
        info = calculate_tithi(search_dt)
        
        # Check if we're in the target tithi
        if info["number"] == target_absolute:
            # Found the tithi, now find its start
            return find_tithi_start(search_dt)
        
        # Check if we're before the target tithi
        current_absolute = info["number"]
        
        # Move forward by roughly 12 hours (half a tithi)
        search_dt += timedelta(hours=12)
    
    return None


def find_tithi_in_month(
    target_tithi: int,
    target_paksha: str,
    year: int,
    month: int
) -> Optional[datetime]:
    """
    Find a specific tithi within a calendar month.
    
    Args:
        target_tithi: Tithi number 1-15
        target_paksha: "shukla" or "krishna"
        year: Gregorian year
        month: Gregorian month (1-12)
    
    Returns:
        Datetime when the tithi occurs, or None
    """
    start_date = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
    
    # Determine days in month
    if month == 12:
        next_month = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        next_month = datetime(year, month + 1, 1, tzinfo=timezone.utc)
    
    days_in_month = (next_month - start_date).days
    
    return find_next_tithi(
        target_tithi,
        target_paksha,
        after=start_date,
        within_days=days_in_month + 5  # Small buffer
    )


# =============================================================================
# TITHI SEQUENCE
# =============================================================================

def get_tithis_in_range(
    start: datetime,
    end: datetime
) -> List[Tuple[int, str, datetime, datetime]]:
    """
    Get all tithi transitions within a date range.
    
    Args:
        start: Range start
        end: Range end
    
    Returns:
        List of (tithi_number, paksha, start_time, end_time)
    """
    result = []
    
    current = start
    while current < end:
        info = calculate_tithi(current)
        tithi_start = find_tithi_start(current)
        tithi_end = find_tithi_end(current)
        
        paksha = "shukla" if info["number"] <= 15 else "krishna"
        display = info["number"] if info["number"] <= 15 else info["number"] - 15
        
        result.append((display, paksha, max(tithi_start, start), min(tithi_end, end)))
        
        # Move to next tithi
        current = tithi_end + timedelta(minutes=1)
    
    return result


# =============================================================================
# TITHI DURATION
# =============================================================================

def get_tithi_duration(tithi_start: datetime, tithi_end: datetime) -> timedelta:
    """Calculate duration of a tithi."""
    return tithi_end - tithi_start


def estimate_average_tithi_duration() -> timedelta:
    """
    Estimate average tithi duration from current ephemeris behavior.

    Uses three recent tithi windows around the current UTC time and
    returns their arithmetic mean duration.
    """
    now = datetime.now(timezone.utc)
    samples = []

    cursor = now
    for _ in range(3):
        start = find_tithi_start(cursor)
        end = find_tithi_end(cursor)
        samples.append((end - start).total_seconds())
        cursor = end + timedelta(minutes=5)

    avg_seconds = sum(samples) / len(samples)
    return timedelta(seconds=avg_seconds)
