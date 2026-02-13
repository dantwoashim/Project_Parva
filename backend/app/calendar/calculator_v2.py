"""
Festival Calculator V2 for Project Parva

Uses the CORRECT lunar month model:
- Computes Amavasya→Amavasya month windows
- Names months by Sun's rashi at Purnima
- Marks Adhik months (no sankranti)
- Uses lunar_month_name in rules, not bs_month
- Applies adhik_policy to skip intercalary months

This fixes the mid-year festival discrepancies caused by Adhik Maas.
"""

import json
from datetime import date, timedelta, datetime, timezone
from pathlib import Path
from typing import Dict, Optional, List, Literal, Tuple
from dataclasses import dataclass

from .lunar_calendar import (
    get_lunar_year,
    find_festival_in_lunar_month,
    LUNAR_MONTH_NAMES,
)
from .bikram_sambat import bs_to_gregorian
from .sankranti import find_mesh_sankranti, find_makara_sankranti


# =============================================================================
# FESTIVAL RULES V3 LOADER
# =============================================================================

@dataclass
class FestivalRuleV3:
    """Festival rule using lunar_month model."""
    name_en: str
    name_ne: str
    type: Literal["solar", "lunar"]
    # For lunar festivals
    lunar_month: Optional[str] = None
    tithi: Optional[int] = None
    paksha: Optional[str] = None
    adhik_policy: str = "skip"
    # For solar festivals
    bs_month: Optional[int] = None
    solar_day: Optional[int] = None
    # Common
    duration_days: int = 1
    notes: str = ""
    importance: str = "national"
    category: str = "hindu"


def load_festival_rules_v3() -> Dict[str, FestivalRuleV3]:
    """Load V3 festival rules with lunar_month support."""
    rules_path = Path(__file__).parent / "festival_rules_v3.json"
    
    if not rules_path.exists():
        # Fallback to empty dict
        return {}
    
    with open(rules_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    rules = {}
    for fid, rule_data in data.get("festivals", {}).items():
        rules[fid] = FestivalRuleV3(
            name_en=rule_data.get("name_en", fid),
            name_ne=rule_data.get("name_ne", ""),
            type=rule_data.get("type", "lunar"),
            lunar_month=rule_data.get("lunar_month"),
            tithi=rule_data.get("tithi"),
            paksha=rule_data.get("paksha"),
            adhik_policy=rule_data.get("adhik_policy", "skip"),
            bs_month=rule_data.get("bs_month"),
            solar_day=rule_data.get("solar_day"),
            duration_days=rule_data.get("duration_days", 1),
            notes=rule_data.get("notes", ""),
            importance=rule_data.get("importance", "national"),
            category=rule_data.get("category", "hindu"),
        )
    
    return rules


# Cache rules
_rules_cache: Optional[Dict[str, FestivalRuleV3]] = None


def get_festival_rules_v3() -> Dict[str, FestivalRuleV3]:
    """Get cached festival rules."""
    global _rules_cache
    if _rules_cache is None:
        _rules_cache = load_festival_rules_v3()
    return _rules_cache


# =============================================================================
# FESTIVAL DATE CALCULATION
# =============================================================================

@dataclass
class FestivalDate:
    """Result of festival date calculation."""
    festival_id: str
    start_date: date
    end_date: date
    year: int
    method: str  # "lunar_month" or "solar" or "fallback"
    lunar_month: Optional[str] = None
    is_adhik_year: bool = False
    
    @property
    def duration_days(self) -> int:
        return (self.end_date - self.start_date).days + 1

    def overlaps(self, target_date: date) -> bool:
        """Return True if target_date falls within the festival range."""
        return self.start_date <= target_date <= self.end_date


def calculate_festival_date_v2(
    festival_id: str,
    year: int,
    use_overrides: bool = True
) -> Optional[FestivalDate]:
    """
    Calculate festival date using the CORRECT lunar month model.
    
    Args:
        festival_id: Festival identifier
        year: Gregorian year
    
    Returns:
        FestivalDate with computed date, or None if not found
    """
    if use_overrides:
        # Authoritative overrides (official dates) when available
        try:
            from .overrides import get_festival_override
            override_date = get_festival_override(festival_id, year)
            if override_date:
                rules = get_festival_rules_v3()
                rule = rules.get(festival_id)
                duration = rule.duration_days if rule else 1
                return FestivalDate(
                    festival_id=festival_id,
                    start_date=override_date,
                    end_date=override_date + timedelta(days=duration - 1),
                    year=year,
                    method="override",
                    lunar_month=rule.lunar_month if rule else None,
                    is_adhik_year=get_lunar_year(year).has_adhik,
                )
        except Exception:
            # Fall back to algorithmic calculation
            pass
    
    rules = get_festival_rules_v3()
    
    if festival_id not in rules:
        # Fallback to legacy rule set (bs_month-based) if available
        try:
            from .calculator import calculate_festival_date as calculate_festival_date_v1
            dr = calculate_festival_date_v1(festival_id, year, use_overrides=use_overrides)
            return FestivalDate(
                festival_id=festival_id,
                start_date=dr.start,
                end_date=dr.end,
                year=year,
                method="fallback_v1",
                lunar_month=None,
                is_adhik_year=get_lunar_year(year).has_adhik,
            )
        except Exception:
            return None
    
    rule = rules[festival_id]
    
    if rule.type == "solar":
        return _calculate_solar_festival(festival_id, rule, year)
    else:
        return _calculate_lunar_festival(festival_id, rule, year)


def _calculate_solar_festival(
    festival_id: str,
    rule: FestivalRuleV3,
    year: int
) -> Optional[FestivalDate]:
    """Calculate solar festival using sankranti."""
    
    if festival_id == "maghe-sankranti" or rule.bs_month == 10:
        # Makara Sankranti
        sankranti_dt = find_makara_sankranti(year)
        if sankranti_dt:
            start_date = sankranti_dt.date()
            return FestivalDate(
                festival_id=festival_id,
                start_date=start_date,
                end_date=start_date + timedelta(days=rule.duration_days - 1),
                year=year,
                method="solar",
            )
    
    elif festival_id == "bs-new-year" or rule.bs_month == 1:
        # Mesh Sankranti (BS New Year)
        sankranti_dt = find_mesh_sankranti(year)
        if sankranti_dt:
            start_date = sankranti_dt.date()
            return FestivalDate(
                festival_id=festival_id,
                start_date=start_date,
                end_date=start_date + timedelta(days=rule.duration_days - 1),
                year=year,
                method="solar",
            )
    
    # Generic solar festival using BS calendar
    if rule.bs_month and rule.solar_day:
        bs_year = year + 56 if year > 1943 else year + 57
        try:
            start_date = bs_to_gregorian(bs_year, rule.bs_month, rule.solar_day)
            return FestivalDate(
                festival_id=festival_id,
                start_date=start_date,
                end_date=start_date + timedelta(days=rule.duration_days - 1),
                year=year,
                method="solar",
            )
        except Exception:
            pass
    
    return None


def _calculate_lunar_festival(
    festival_id: str,
    rule: FestivalRuleV3,
    year: int
) -> Optional[FestivalDate]:
    """
    Calculate lunar festival using the CORRECT lunar month model.
    
    This properly handles Adhik Maas by:
    1. Building the lunar year to identify Adhik months
    2. Using lunar_month_name to find the correct month
    3. Applying adhik_policy to skip or use Adhik months
    4. Using udaya tithi for final date determination
    """
    if not rule.lunar_month or not rule.tithi or not rule.paksha:
        return None
    
    # Get lunar year to check for Adhik
    lunar_year = get_lunar_year(year)
    
    # Find festival date using lunar month model
    festival_date = find_festival_in_lunar_month(
        lunar_month_name=rule.lunar_month,
        tithi=rule.tithi,
        paksha=rule.paksha,
        gregorian_year=year,
        adhik_policy=rule.adhik_policy,
    )
    
    if festival_date is None:
        return None
    
    return FestivalDate(
        festival_id=festival_id,
        start_date=festival_date,
        end_date=festival_date + timedelta(days=rule.duration_days - 1),
        year=year,
        method="lunar_month",
        lunar_month=rule.lunar_month,
        is_adhik_year=lunar_year.has_adhik,
    )


# =============================================================================
# PUBLIC API
# =============================================================================

def calculate_festival_v2(
    festival_id: str,
    year: int,
    use_overrides: bool = True
) -> Optional[FestivalDate]:
    """
    Public API: Calculate festival date with correct Adhik handling.
    
    This is the V2 calculator that uses lunar_month model.
    """
    return calculate_festival_date_v2(festival_id, year, use_overrides=use_overrides)


def list_festivals_v2() -> List[str]:
    """
    List all festivals supported by V2 engine.
    
    Includes V3 lunar-month rules and fallback legacy rules (festival_rules.json).
    """
    ids = set(get_festival_rules_v3().keys())
    try:
        from .festival_rules_loader import list_festivals
        ids.update(list_festivals())
    except Exception:
        pass
    return sorted(ids)


def get_festival_info_v2(festival_id: str) -> Optional[FestivalRuleV3]:
    """Get festival rule info."""
    rules = get_festival_rules_v3()
    return rules.get(festival_id)


def get_upcoming_festivals_v2(
    from_date: date,
    days: int = 30
) -> List[Tuple[str, FestivalDate]]:
    """
    Get all festivals occurring within a date range using V2 engine.
    """
    end_date = from_date + timedelta(days=days)
    results: List[Tuple[str, FestivalDate]] = []

    years_to_check = {from_date.year, end_date.year}

    for festival_id in list_festivals_v2():
        for year in years_to_check:
            try:
                date_range = calculate_festival_v2(festival_id, year)
                if date_range and date_range.end_date >= from_date and date_range.start_date <= end_date:
                    results.append((festival_id, date_range))
            except Exception:
                continue

    results.sort(key=lambda x: x[1].start_date)

    # Deduplicate
    seen = set()
    unique_results = []
    for festival_id, date_range in results:
        key = (festival_id, date_range.start_date)
        if key not in seen:
            seen.add(key)
            unique_results.append((festival_id, date_range))

    return unique_results


def get_festivals_on_date_v2(target_date: date) -> List[Tuple[str, FestivalDate]]:
    """
    Get all festivals occurring on a specific date using V2 engine.
    """
    results: List[Tuple[str, FestivalDate]] = []

    for festival_id in list_festivals_v2():
        try:
            date_range = calculate_festival_v2(festival_id, target_date.year)
            if date_range and date_range.overlaps(target_date):
                results.append((festival_id, date_range))
        except Exception:
            continue

    return results


def get_next_occurrence_v2(
    festival_id: str,
    after_date: Optional[date] = None
) -> Optional[FestivalDate]:
    """
    Get the next occurrence of a specific festival using V2 engine.
    """
    if after_date is None:
        after_date = date.today()

    for year in [after_date.year, after_date.year + 1, after_date.year + 2]:
        try:
            date_range = calculate_festival_v2(festival_id, year)
            if date_range and date_range.start_date > after_date:
                return date_range
            if date_range and date_range.overlaps(after_date):
                return date_range
        except Exception:
            continue
    return None
