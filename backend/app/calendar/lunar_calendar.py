"""
Lunar Calendar Module for Project Parva v2.0

Builds a properly-structured lunar calendar with:
- Amavasya→Amavasya month windows
- Solar-based month naming (Sun's rashi at Purnima)
- Adhik Maas detection (no sankranti in month)
- Nija/Adhik distinction for festival calculation

This is the CORRECT model for handling lunar festivals in Adhik years.
"""

from datetime import datetime, date, timedelta, timezone
from typing import List, Dict, Optional, NamedTuple, Literal
from dataclasses import dataclass

from .adhik_maas import find_amavasya, find_purnima, is_adhik_maas, get_lunar_month_name
from .sankranti import get_sun_rashi_at_time, find_sankranti, BS_MONTH_NAMES
from .tithi import find_next_tithi, get_udaya_tithi
from .ephemeris.time_utils import NEPAL_TZ


# =============================================================================
# LUNAR MONTH DATA STRUCTURES
# =============================================================================

@dataclass
class LunarMonth:
    """
    Represents a single lunar month using AMANTA (new moon ending) structure.
    
    IMPORTANT: This uses Amavasya→Amavasya boundaries for internal tracking,
    but NAMING follows Purnimant convention (month named by its Purnima).
    
    Structure:
    - Shukla paksha (1-15): start_amavasya to end_purnima (named by this month)
    - Krishna paksha (1-15): end_purnima to end_amavasya (named by this month)
    
    Month naming: Uses Sun's rashi at this month's Purnima (end_purnima).
    """
    # Time boundaries
    start_amavasya: datetime  # New moon that starts this month
    end_purnima: datetime     # Full moon that ends this month (for Purnimant)
    end_amavasya: datetime    # Next new moon (actual month end)
    
    # Month identity
    month_name: str           # Sanskrit name (Baisakh, Jestha, etc.)
    month_index: int          # 1-12 for regular months
    is_adhik: bool            # True if this is Adhik (intercalary) month
    
    # Solar context
    sun_rashi_at_purnima: int  # Rashi (0-11) when Purnima occurs
    sankranti_date: Optional[datetime] = None  # Sankranti in this month (if any)
    
    @property
    def type(self) -> str:
        """Return 'adhik' or 'nija'."""
        return "adhik" if self.is_adhik else "nija"
    
    @property
    def full_name(self) -> str:
        """Full name including Adhik/Nija prefix."""
        if self.is_adhik:
            return f"Adhik {self.month_name}"
        return self.month_name
    
    def contains_date(self, dt: datetime) -> bool:
        """Check if a datetime falls within this lunar month."""
        return self.start_amavasya <= dt < self.end_amavasya
    
    def contains_tithi(self, tithi: int, paksha: str) -> bool:
        """Check if this month contains the specified tithi."""
        # All months have all tithis, but we need to determine if the 
        # tithi occurs within the month's date range
        return True  # Simplified; actual check done during search


@dataclass
class LunarYear:
    """
    A complete lunar year with all months.
    
    A lunar year typically has 12 months, but in an Adhik year has 13.
    The year starts roughly around Chaitra/Baisakh (March-April).
    """
    gregorian_year: int        # Approximate Gregorian year
    bs_year: int               # Corresponding BS year
    months: List[LunarMonth]   # All months in order
    has_adhik: bool            # Whether this year has an Adhik month
    adhik_month_name: Optional[str] = None  # Which month is doubled
    
    def get_month(self, month_name: str, prefer_nija: bool = True) -> Optional[LunarMonth]:
        """
        Get a month by name.
        
        For Adhik years, if prefer_nija is True, returns the Nija month
        (the "real" month, not the intercalary one).
        """
        matches = [m for m in self.months if m.month_name == month_name]
        
        if not matches:
            return None
        
        if len(matches) == 1:
            return matches[0]
        
        # Two matches = Adhik and Nija
        if prefer_nija:
            return next((m for m in matches if not m.is_adhik), matches[-1])
        else:
            return next((m for m in matches if m.is_adhik), matches[0])


# =============================================================================
# LUNAR MONTH COMPUTATION
# =============================================================================

def name_lunar_month(start_amavasya: datetime, end_amavasya: datetime) -> str:
    """
    Name a lunar month using Sun's rashi at the month's Purnima.

    Args:
        start_amavasya: month start instant
        end_amavasya: month end instant

    Returns:
        Month name aligned with current festival rule naming.
    """
    search_start = start_amavasya + timedelta(days=2)
    purnima = find_purnima(search_start)
    if purnima is None or purnima >= end_amavasya:
        # Fallback midpoint search if direct purnima detection misses boundaries.
        midpoint = start_amavasya + (end_amavasya - start_amavasya) / 2
        purnima = find_purnima(midpoint - timedelta(days=3)) or midpoint

    sun_rashi = get_sun_rashi_at_time(purnima)
    return BS_MONTH_NAMES[sun_rashi]


def detect_adhik_maas(month_start: datetime, month_end: datetime) -> bool:
    """
    Wrapper for adhik-maas detection with explicit lunar-month semantics.
    """
    return is_adhik_maas(month_start, month_end)


def lunar_month_boundaries(gregorian_year: int) -> List[tuple[datetime, datetime]]:
    """
    Compute Amavasya->Amavasya month boundaries intersecting a Gregorian year.

    Returns:
        List of `(start_amavasya, end_amavasya)` tuples.
    """
    # Start slightly before year to capture crossing boundaries.
    cursor = datetime(gregorian_year - 1, 12, 1, tzinfo=timezone.utc)
    boundaries: List[tuple[datetime, datetime]] = []

    # Build up to 18 months to safely cover the year with adhik cases.
    start = find_amavasya(cursor)
    for _ in range(18):
        if start is None:
            break
        # Search from +1 day so we always get the *next* amavasya boundary.
        end = find_amavasya(start + timedelta(days=1))
        if end is None:
            break
        # Keep months touching the requested year.
        if start.year <= gregorian_year <= end.year:
            boundaries.append((start, end))
        # Month windows are contiguous by definition (end == next start).
        start = end
        if start.year > gregorian_year and len(boundaries) >= 12:
            break

    return boundaries

def compute_lunar_month(
    start_amavasya: datetime,
    month_number: int = 0
) -> LunarMonth:
    """
    Compute a single lunar month starting from an Amavasya.
    
    Args:
        start_amavasya: The Amavasya that begins this month
        month_number: Sequential month number (for tracking)
    
    Returns:
        LunarMonth with all computed properties
    """
    # Find the Purnima in this month (about 15 days later)
    purnima = find_purnima(start_amavasya + timedelta(days=2))
    if purnima is None:
        raise ValueError(f"Could not find Purnima after {start_amavasya}")
    
    # Find the next Amavasya (end of this month in Amant)
    next_amavasya = find_amavasya(purnima + timedelta(days=2))
    if next_amavasya is None:
        raise ValueError(f"Could not find Amavasya after {purnima}")
    
    sun_rashi = get_sun_rashi_at_time(purnima)
    month_name = name_lunar_month(start_amavasya, next_amavasya)
    
    # Check for Adhik Maas (no sankranti in this month)
    # Must pass both start and end of the lunar month
    is_adhik = detect_adhik_maas(start_amavasya, next_amavasya)
    
    # Find sankranti in this month (if any)
    sankranti = None
    for target_rashi in range(12):
        s = find_sankranti(target_rashi, start_amavasya, max_days=35)
        if s and start_amavasya <= s < next_amavasya:
            sankranti = s
            break
    
    return LunarMonth(
        start_amavasya=start_amavasya,
        end_purnima=purnima,
        end_amavasya=next_amavasya,
        month_name=month_name,
        month_index=(sun_rashi + 1) if sun_rashi < 12 else 1,
        is_adhik=is_adhik,
        sun_rashi_at_purnima=sun_rashi,
        sankranti_date=sankranti
    )


def build_lunar_year(gregorian_year: int) -> LunarYear:
    """
    Build a complete lunar year for a given Gregorian year.
    
    The lunar year roughly aligns with Gregorian but starts around March-April.
    We build months from the Amavasya before Baishakh 1 through 13 months.
    
    Args:
        gregorian_year: The Gregorian year (e.g., 2026)
    
    Returns:
        LunarYear with all months computed
    """
    # Start searching from around March (before Baishakh/Chaitra)
    search_start = datetime(gregorian_year, 2, 15, tzinfo=timezone.utc)
    
    # Find the first Amavasya around late Chaitra (before new BS year)
    first_amavasya = find_amavasya(search_start)
    if first_amavasya is None:
        raise ValueError(f"Could not find starting Amavasya for {gregorian_year}")
    
    # Build 13 months (to cover Adhik case)
    months: List[LunarMonth] = []
    current_amavasya = first_amavasya
    
    for i in range(14):  # 14 to ensure we cover a full year
        try:
            month = compute_lunar_month(current_amavasya, i)
            months.append(month)
            current_amavasya = month.end_amavasya
            
            # Stop if we've gone past the year
            if current_amavasya.year > gregorian_year + 1:
                break
        except ValueError:
            break
    
    # Check for Adhik month
    has_adhik = any(m.is_adhik for m in months)
    adhik_name = next((m.month_name for m in months if m.is_adhik), None)
    
    # Determine BS year (roughly Gregorian year + 57)
    bs_year = gregorian_year + 56 if first_amavasya.month < 4 else gregorian_year + 57
    
    return LunarYear(
        gregorian_year=gregorian_year,
        bs_year=bs_year,
        months=months,
        has_adhik=has_adhik,
        adhik_month_name=adhik_name
    )


# Cache for computed lunar years
_lunar_year_cache: Dict[int, LunarYear] = {}


def get_lunar_year(gregorian_year: int) -> LunarYear:
    """
    Get or compute a lunar year (with caching).
    
    Args:
        gregorian_year: Gregorian year
    
    Returns:
        LunarYear for that year
    """
    if gregorian_year not in _lunar_year_cache:
        _lunar_year_cache[gregorian_year] = build_lunar_year(gregorian_year)
    return _lunar_year_cache[gregorian_year]


# =============================================================================
# FESTIVAL DATE FINDING (Correct Model)
# =============================================================================

def find_festival_in_lunar_month(
    lunar_month_name: str,
    tithi: int,
    paksha: str,
    gregorian_year: int,
    adhik_policy: Literal["skip", "use_adhik", "both"] = "skip"
) -> Optional[date]:
    """
    Find a festival date using the CORRECT lunar month model.
    
    This searches BOTH the current and previous year's lunar calendars
    because festivals in early Gregorian months (Jan-Apr) may fall in
    the previous year's lunar calendar.
    
    Args:
        lunar_month_name: Month name (e.g., "Bhadra", "Ashwin")
        tithi: Target tithi 1-15
        paksha: "shukla" or "krishna"
        gregorian_year: Gregorian year for the festival
        adhik_policy: How to handle Adhik months
    
    Returns:
        Gregorian date of the festival, or None if not found
    """
    # Search both current year and previous year's lunar calendars
    # because early-year festivals (Jan-Apr) may be in prev lunar year
    candidates = []  # List of (date, is_adhik_month) tuples
    
    for search_year in [gregorian_year - 1, gregorian_year]:
        lunar_year = get_lunar_year(search_year)
        
        # Find all months with this name (could be 1 or 2 if Adhik)
        matching_months = [m for m in lunar_year.months if m.month_name == lunar_month_name]
        
        for month in matching_months:
            # Apply adhik_policy
            if adhik_policy == "skip" and month.is_adhik:
                continue  # Skip Adhik month, use Nija only
            elif adhik_policy == "use_adhik" and not month.is_adhik:
                # Only use Adhik if it exists; skip Nija
                # But if no Adhik exists, we'll fall through to use Nija
                if any(m.is_adhik for m in matching_months):
                    continue
            # "both" policy: include both Adhik and Nija
            
            # Search for tithi in this month
            result = _search_tithi_in_month(month, tithi, paksha, gregorian_year)
            if result:
                candidates.append((result, month.is_adhik))
    
    if not candidates:
        return None
    
    # Return the candidate that's in the target Gregorian year
    # Prefer Nija over Adhik unless policy says otherwise
    for result_date, is_adhik in candidates:
        if result_date.year == gregorian_year:
            if adhik_policy == "use_adhik":
                if is_adhik:
                    return result_date
            else:
                return result_date
    
    # Fallback to first matching result
    return candidates[0][0]


def _search_tithi_in_month(
    month: LunarMonth,
    tithi: int,
    paksha: str,
    target_year: int
) -> Optional[date]:
    """Search for a specific tithi within a lunar month."""
    
    # For Shukla paksha (waxing): search from month start (Amavasya)
    # For Krishna paksha (waning): search from Purnima (middle of month)
    if paksha == "shukla":
        search_start = month.start_amavasya
    else:
        # Krishna paksha starts after Purnima
        search_start = month.end_purnima
    
    search_end = month.end_amavasya
    
    # Find the tithi in this month
    tithi_datetime = find_next_tithi(
        tithi, paksha,
        search_start,
        within_days=35
    )
    
    if tithi_datetime is None:
        return None
    
    # For Krishna 15, allow it to be exactly at month end (Amavasya is the boundary)
    if paksha == "krishna" and tithi == 15:
        # Allow up to 1 day after end_amavasya for boundary tithis
        if not (search_start <= tithi_datetime <= month.end_amavasya + timedelta(hours=24)):
            return None
    else:
        # Ensure it's within this month's boundaries
        if not (search_start <= tithi_datetime < search_end):
            return None
    
    candidate_date = tithi_datetime.date()
    
    # Use udaya tithi to get the exact festival date
    # MUST find udaya match; no fallback to avoid off-by-one errors
    for offset in range(5):  # Check 5 days to handle edge cases
        check_date = candidate_date + timedelta(days=offset - 1)  # Start 1 day before
        try:
            udaya = get_udaya_tithi(check_date)
            if udaya["tithi"] == tithi and udaya["paksha"] == paksha:
                return check_date
        except Exception:
            continue
    
    # No udaya match found - return None instead of unreliable fallback
    return None


# =============================================================================
# MONTH NAME MAPPINGS
# =============================================================================

# Lunar month names (must match festival_rules_v3.json spelling)
LUNAR_MONTH_NAMES = [
    "Baishakh",   # 1 - April-May (note: 'sh' spelling to match rules)
    "Jestha",     # 2 - May-June
    "Ashadh",     # 3 - June-July
    "Shrawan",    # 4 - July-August
    "Bhadra",     # 5 - August-September
    "Ashwin",     # 6 - September-October
    "Kartik",     # 7 - October-November
    "Mangsir",    # 8 - November-December
    "Poush",      # 9 - December-January
    "Magh",       # 10 - January-February
    "Falgun",     # 11 - February-March
    "Chaitra",    # 12 - March-April
]


def get_lunar_month_index(name: str) -> int:
    """Get 1-based index for a lunar month name."""
    name_lower = name.lower()
    for i, m in enumerate(LUNAR_MONTH_NAMES):
        if m.lower() == name_lower:
            return i + 1
    raise ValueError(f"Unknown lunar month: {name}")


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def print_lunar_year(year: int):
    """Print a lunar year for debugging."""
    ly = get_lunar_year(year)
    print(f"\nLunar Year for {year} (BS {ly.bs_year})")
    print(f"Has Adhik: {ly.has_adhik} ({ly.adhik_month_name or 'N/A'})")
    print("-" * 60)
    
    for i, m in enumerate(ly.months):
        adhik_mark = " [ADHIK]" if m.is_adhik else ""
        sankranti_info = f", Sankranti: {m.sankranti_date.date()}" if m.sankranti_date else ""
        print(f"{i+1:2}. {m.full_name:15} | {m.start_amavasya.date()} to {m.end_amavasya.date()}{adhik_mark}{sankranti_info}")
