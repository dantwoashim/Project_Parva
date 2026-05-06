"""Civil-date assignment rules for solar-ingress month starts."""

from __future__ import annotations

from datetime import date, timedelta
from functools import lru_cache

from app.calendar.ephemeris.swiss_eph import calculate_sunrise
from app.calendar.ephemeris.time_utils import to_nepal_time

from .models import SolarIngressEvent


def same_nepal_civil_date(event: SolarIngressEvent) -> date:
    return event.nepal_date


@lru_cache(maxsize=2048)
def _sunrise_for_nepal_date(local_date: date):
    return to_nepal_time(calculate_sunrise(local_date))


def sunrise_rule(event: SolarIngressEvent) -> date:
    sunrise_local = _sunrise_for_nepal_date(event.nepal_date)
    if event.datetime_nepal <= sunrise_local:
        return event.nepal_date
    return event.nepal_date + timedelta(days=1)


ASSIGNMENT_RULES = {
    "same_nepal_civil_date": same_nepal_civil_date,
    "sunrise_rule": sunrise_rule,
}
