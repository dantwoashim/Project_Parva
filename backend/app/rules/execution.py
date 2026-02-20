"""Deterministic rule execution for v4 DSL-compatible festival rules.

This module provides a lightweight executor used by:
- Month-2 validation triads
- computed-rule promotion checks
- future generic rule-evaluation endpoints
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional

from app.calendar.bikram_sambat import bs_to_gregorian, gregorian_to_bs
from app.calendar.calculator_v2 import calculate_festival_v2
from app.calendar.lunar_calendar import find_festival_in_lunar_month
from app.calendar.sankranti import find_makara_sankranti, find_mesh_sankranti
from app.calendar.tithi.tithi_boundaries import find_next_tithi as find_next_tithi_boundary

from .schema_v4 import FestivalRuleV4


_LUNAR_MONTH_ALIASES = {
    "baisakh": "Baishakh",
    "baishakh": "Baishakh",
    "jestha": "Jestha",
    "ashadh": "Ashadh",
    "shrawan": "Shrawan",
    "shravan": "Shrawan",
    "bhadra": "Bhadra",
    "ashwin": "Ashwin",
    "kartik": "Kartik",
    "mangsir": "Mangsir",
    "poush": "Poush",
    "magh": "Magh",
    "falgun": "Falgun",
    "chaitra": "Chaitra",
}


@dataclass
class RuleExecutionResult:
    festival_id: str
    year: int
    start_date: date
    end_date: date
    method: str

    @property
    def duration_days(self) -> int:
        return (self.end_date - self.start_date).days + 1


def _duration(rule: FestivalRuleV4) -> int:
    raw = (rule.rule or {}).get("duration_days", 1)
    try:
        return max(int(raw), 1)
    except Exception:
        return 1


def _bs_year_for_month(gregorian_year: int, bs_month: int) -> int:
    # BS months 10-12 usually fall in Jan-Mar of AD year.
    return gregorian_year + (56 if bs_month >= 10 else 57)


def _normalize_lunar_month(value: Any) -> Optional[str]:
    if not value:
        return None
    key = str(value).strip()
    if not key:
        return None
    return _LUNAR_MONTH_ALIASES.get(key.lower(), key)


def _to_int(value: Any) -> Optional[int]:
    try:
        if value is None or value == "":
            return None
        return int(value)
    except Exception:
        return None


def _compute_lunar(rule: FestivalRuleV4, year: int) -> RuleExecutionResult | None:
    payload = rule.rule or {}
    tithi = _to_int(payload.get("tithi"))
    paksha = str(payload.get("paksha") or "").strip().lower()
    if not tithi or paksha not in {"shukla", "krishna"}:
        return None

    duration = _duration(rule)

    lunar_month = _normalize_lunar_month(payload.get("lunar_month"))
    if lunar_month:
        start = find_festival_in_lunar_month(
            lunar_month_name=lunar_month,
            tithi=tithi,
            paksha=paksha,
            gregorian_year=year,
            adhik_policy=str(payload.get("adhik_policy") or "skip"),
        )
        if start:
            return RuleExecutionResult(
                festival_id=rule.festival_id,
                year=year,
                start_date=start,
                end_date=start + timedelta(days=duration - 1),
                method="rule_dsl_lunar_month_v1",
            )

    bs_month = _to_int(payload.get("bs_month"))
    if not bs_month:
        return None

    bs_year = _bs_year_for_month(year, bs_month)
    month_start: date | None = None
    for candidate_year in (bs_year, bs_year - 1, bs_year + 1):
        try:
            month_start = bs_to_gregorian(candidate_year, bs_month, 1)
            break
        except Exception:
            continue
    if month_start is None:
        return None

    search_start = month_start - timedelta(days=2)
    search_after = datetime.combine(search_start, datetime.min.time()).replace(tzinfo=timezone.utc)

    found_date: date | None = None
    for _ in range(3):
        found_dt = find_next_tithi_boundary(
            target_tithi=tithi,
            target_paksha=paksha,
            after=search_after,
            within_days=62,
        )
        if found_dt is None:
            break

        candidate = found_dt.date()
        try:
            _, candidate_month, _ = gregorian_to_bs(candidate)
        except Exception:
            candidate_month = None

        if candidate_month == bs_month:
            found_date = candidate
            break

        search_after = found_dt + timedelta(days=1)

    if found_date is None:
        return None

    return RuleExecutionResult(
        festival_id=rule.festival_id,
        year=year,
        start_date=found_date,
        end_date=found_date + timedelta(days=duration - 1),
        method="rule_dsl_lunar_bs_month_v1",
    )


def _compute_solar(rule: FestivalRuleV4, year: int) -> RuleExecutionResult | None:
    payload = rule.rule or {}
    duration = _duration(rule)
    event = str(payload.get("event") or "").strip().lower()
    bs_month = _to_int(payload.get("bs_month"))

    if event in {"mesh_sankranti", "new_year", "bs_new_year"}:
        dt = find_mesh_sankranti(year)
        if dt:
            start = dt.date()
            return RuleExecutionResult(
                festival_id=rule.festival_id,
                year=year,
                start_date=start,
                end_date=start + timedelta(days=duration - 1),
                method="rule_dsl_mesh_sankranti_v1",
            )

    if event in {"makara_sankranti", "maghe_sankranti"}:
        dt = find_makara_sankranti(year)
        if dt:
            start = dt.date()
            return RuleExecutionResult(
                festival_id=rule.festival_id,
                year=year,
                start_date=start,
                end_date=start + timedelta(days=duration - 1),
                method="rule_dsl_makara_sankranti_v1",
            )

    if event == "sankranti" and bs_month:
        bs_year = _bs_year_for_month(year, bs_month)
        for candidate_year in (bs_year, bs_year - 1, bs_year + 1):
            try:
                start = bs_to_gregorian(candidate_year, bs_month, 1)
                return RuleExecutionResult(
                    festival_id=rule.festival_id,
                    year=year,
                    start_date=start,
                    end_date=start + timedelta(days=duration - 1),
                    method="rule_dsl_solar_month_start_v1",
                )
            except Exception:
                continue

    solar_day = _to_int(payload.get("solar_day"))
    if bs_month and solar_day:
        bs_year = _bs_year_for_month(year, bs_month)
        for candidate_year in (bs_year, bs_year - 1, bs_year + 1):
            try:
                start = bs_to_gregorian(candidate_year, bs_month, solar_day)
                return RuleExecutionResult(
                    festival_id=rule.festival_id,
                    year=year,
                    start_date=start,
                    end_date=start + timedelta(days=duration - 1),
                    method="rule_dsl_solar_fixed_v1",
                )
            except Exception:
                continue

    return None


def _compute_override(rule: FestivalRuleV4, year: int) -> RuleExecutionResult | None:
    payload = rule.rule or {}
    duration = _duration(rule)

    dates = payload.get("dates")
    if isinstance(dates, dict):
        value = dates.get(str(year))
        if value:
            try:
                start = date.fromisoformat(str(value))
                return RuleExecutionResult(
                    festival_id=rule.festival_id,
                    year=year,
                    start_date=start,
                    end_date=start + timedelta(days=duration - 1),
                    method="rule_dsl_override_lookup_v1",
                )
            except Exception:
                pass

    bs_year = _to_int(payload.get("bs_year"))
    bs_month = _to_int(payload.get("bs_month"))
    bs_day = _to_int(payload.get("bs_day"))
    if bs_year and bs_month and bs_day:
        try:
            start = bs_to_gregorian(bs_year, bs_month, bs_day)
            if start.year == year:
                return RuleExecutionResult(
                    festival_id=rule.festival_id,
                    year=year,
                    start_date=start,
                    end_date=start + timedelta(days=duration - 1),
                    method="rule_dsl_override_bs_fixed_v1",
                )
        except Exception:
            pass

    return None


def calculate_rule_occurrence(rule: FestivalRuleV4, year: int) -> RuleExecutionResult | None:
    """Calculate festival date for a v4 rule in a Gregorian year."""
    if rule.rule_type == "lunar":
        return _compute_lunar(rule, year)
    if rule.rule_type == "solar":
        return _compute_solar(rule, year)
    if rule.rule_type == "override":
        return _compute_override(rule, year)
    return None


def calculate_rule_occurrence_with_fallback(rule: FestivalRuleV4, year: int) -> RuleExecutionResult | None:
    """Calculate rule occurrence with v2 fallback for known rule IDs."""
    direct = calculate_rule_occurrence(rule, year)
    if direct is not None:
        return direct

    try:
        from_v2 = calculate_festival_v2(rule.festival_id, year)
    except Exception:
        from_v2 = None
    if from_v2 is None:
        return None

    return RuleExecutionResult(
        festival_id=rule.festival_id,
        year=year,
        start_date=from_v2.start_date,
        end_date=from_v2.end_date,
        method=f"rule_dsl_v2_fallback:{from_v2.method}",
    )


def validation_cases_for_rule(rule: FestivalRuleV4, years: tuple[int, ...] = (2025, 2026, 2027)) -> list[dict[str, Any]]:
    """Build deterministic validation cases for triad artifacts."""
    cases: list[dict[str, Any]] = []
    for year in years:
        result = calculate_rule_occurrence_with_fallback(rule, year)
        if result is None:
            cases.append(
                {
                    "year": year,
                    "expected_start_date": None,
                    "expected_end_date": None,
                    "method": None,
                    "status": "pending",
                    "note": "No executable path for this year/rule combination.",
                }
            )
            continue
        cases.append(
            {
                "year": year,
                "expected_start_date": result.start_date.isoformat(),
                "expected_end_date": result.end_date.isoformat(),
                "method": result.method,
                "status": "passed",
            }
        )
    return cases
