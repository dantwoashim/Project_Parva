"""Civil-date assignment rules for solar-ingress month starts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from functools import lru_cache

from app.calendar.ephemeris.swiss_eph import calculate_sunrise
from app.calendar.ephemeris.time_utils import NEPAL_TZ, to_nepal_time

from .models import SolarIngressEvent


@dataclass(frozen=True)
class CivilRuleResult:
    rule_name: str
    sankranti_nepal_time: datetime
    assigned_month_start_date: date
    cutoff_used: str
    boundary_distance_minutes: int | None
    rule_confidence: float

    def payload(self) -> dict:
        return {
            "rule_name": self.rule_name,
            "sankranti_nepal_time": self.sankranti_nepal_time.isoformat(),
            "assigned_month_start_date": self.assigned_month_start_date.isoformat(),
            "cutoff_used": self.cutoff_used,
            "boundary_distance_minutes": self.boundary_distance_minutes,
            "rule_confidence": self.rule_confidence,
        }


@lru_cache(maxsize=2048)
def _sunrise_for_nepal_date(local_date: date):
    return to_nepal_time(calculate_sunrise(local_date))


def _fixed_cutoff(event: SolarIngressEvent, cutoff: time, rule_name: str, confidence: float) -> CivilRuleResult:
    local_dt = event.datetime_nepal
    cutoff_dt = datetime.combine(local_dt.date(), cutoff, tzinfo=NEPAL_TZ)
    assigned = local_dt.date() if local_dt <= cutoff_dt else local_dt.date() + timedelta(days=1)
    distance = int(abs((local_dt - cutoff_dt).total_seconds()) // 60)
    return CivilRuleResult(
        rule_name=rule_name,
        sankranti_nepal_time=local_dt,
        assigned_month_start_date=assigned,
        cutoff_used=cutoff.strftime("%H:%M"),
        boundary_distance_minutes=distance,
        rule_confidence=confidence,
    )


def assign_same_day(event: SolarIngressEvent) -> CivilRuleResult:
    return CivilRuleResult(
        rule_name="same_day",
        sankranti_nepal_time=event.datetime_nepal,
        assigned_month_start_date=event.nepal_date,
        cutoff_used="same_nepal_civil_date",
        boundary_distance_minutes=None,
        rule_confidence=0.72,
    )


def assign_next_day_if_after_sunrise(event: SolarIngressEvent) -> CivilRuleResult:
    sunrise_local = _sunrise_for_nepal_date(event.nepal_date)
    assigned = event.nepal_date if event.datetime_nepal <= sunrise_local else event.nepal_date + timedelta(days=1)
    distance = int(abs((event.datetime_nepal - sunrise_local).total_seconds()) // 60)
    return CivilRuleResult(
        rule_name="next_day_if_after_sunrise",
        sankranti_nepal_time=event.datetime_nepal,
        assigned_month_start_date=assigned,
        cutoff_used=sunrise_local.strftime("%H:%M"),
        boundary_distance_minutes=distance,
        rule_confidence=0.74,
    )


def assign_next_day_if_after_noon(event: SolarIngressEvent) -> CivilRuleResult:
    return _fixed_cutoff(event, time(12, 0), "next_day_if_after_noon", 0.68)


def assign_next_day_if_after_sunset(event: SolarIngressEvent) -> CivilRuleResult:
    return _fixed_cutoff(event, time(18, 0), "next_day_if_after_sunset", 0.64)


def assign_fixed_cutoff_06_00(event: SolarIngressEvent) -> CivilRuleResult:
    return _fixed_cutoff(event, time(6, 0), "fixed_cutoff_06_00", 0.66)


def assign_fixed_cutoff_12_00(event: SolarIngressEvent) -> CivilRuleResult:
    return _fixed_cutoff(event, time(12, 0), "fixed_cutoff_12_00", 0.68)


def assign_fixed_cutoff_18_00(event: SolarIngressEvent) -> CivilRuleResult:
    return _fixed_cutoff(event, time(18, 0), "fixed_cutoff_18_00", 0.64)


MONTH_SPECIFIC_CUTOFFS = {
    1: time(12, 0),
    2: time(12, 0),
    3: time(12, 0),
    4: time(12, 0),
    5: time(18, 0),
    6: time(18, 0),
    7: time(6, 0),
    8: time(6, 0),
    9: time(6, 0),
    10: time(6, 0),
    11: time(6, 0),
    12: time(12, 0),
}


def assign_month_specific_cutoff(event: SolarIngressEvent) -> CivilRuleResult:
    cutoff = MONTH_SPECIFIC_CUTOFFS.get(event.bs_month, time(12, 0))
    return _fixed_cutoff(event, cutoff, "month_specific_cutoff", 0.7)


def assign_learned_cutoff(event: SolarIngressEvent) -> CivilRuleResult:
    # Current learned candidate is intentionally conservative and aliases the
    # month-specific cutoffs until calibration writes a stronger rule table.
    result = assign_month_specific_cutoff(event)
    return CivilRuleResult(
        rule_name="learned_cutoff",
        sankranti_nepal_time=result.sankranti_nepal_time,
        assigned_month_start_date=result.assigned_month_start_date,
        cutoff_used=result.cutoff_used,
        boundary_distance_minutes=result.boundary_distance_minutes,
        rule_confidence=0.7,
    )


def assign_era_specific_rule(event: SolarIngressEvent) -> CivilRuleResult:
    result = assign_learned_cutoff(event)
    return CivilRuleResult(
        rule_name="era_specific_rule",
        sankranti_nepal_time=result.sankranti_nepal_time,
        assigned_month_start_date=result.assigned_month_start_date,
        cutoff_used=result.cutoff_used,
        boundary_distance_minutes=result.boundary_distance_minutes,
        rule_confidence=0.68,
    )


def assign_boundary_sensitive_rule(event: SolarIngressEvent) -> CivilRuleResult:
    sunrise = assign_next_day_if_after_sunrise(event)
    if sunrise.boundary_distance_minutes is not None and sunrise.boundary_distance_minutes <= 120:
        return sunrise
    return assign_learned_cutoff(event)


RULE_ASSIGNERS = {
    "same_day": assign_same_day,
    "same_nepal_civil_date": assign_same_day,
    "next_day_if_after_sunrise": assign_next_day_if_after_sunrise,
    "sunrise_rule": assign_next_day_if_after_sunrise,
    "next_day_if_after_noon": assign_next_day_if_after_noon,
    "next_day_if_after_sunset": assign_next_day_if_after_sunset,
    "fixed_cutoff_06_00": assign_fixed_cutoff_06_00,
    "fixed_cutoff_12_00": assign_fixed_cutoff_12_00,
    "fixed_cutoff_18_00": assign_fixed_cutoff_18_00,
    "month_specific_cutoff": assign_month_specific_cutoff,
    "learned_cutoff": assign_learned_cutoff,
    "era_specific_rule": assign_era_specific_rule,
    "boundary_sensitive_rule": assign_boundary_sensitive_rule,
}


def assign_with_rule(event: SolarIngressEvent, rule_name: str) -> CivilRuleResult:
    try:
        return RULE_ASSIGNERS[rule_name](event)
    except KeyError as exc:
        raise ValueError(f"Unknown civil rule: {rule_name}") from exc


def _date_only(rule_name: str):
    def assign(event: SolarIngressEvent) -> date:
        return assign_with_rule(event, rule_name).assigned_month_start_date

    return assign


ASSIGNMENT_RULES = {
    "same_nepal_civil_date": _date_only("same_nepal_civil_date"),
    "sunrise_rule": _date_only("sunrise_rule"),
    "next_day_if_after_noon": _date_only("next_day_if_after_noon"),
    "fixed_cutoff_18_00": _date_only("fixed_cutoff_18_00"),
    "month_specific_cutoff": _date_only("month_specific_cutoff"),
    "learned_cutoff": _date_only("learned_cutoff"),
    "boundary_sensitive_rule": _date_only("boundary_sensitive_rule"),
}
