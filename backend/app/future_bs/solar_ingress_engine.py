"""Solar-ingress event extraction for BS month boundaries."""

from __future__ import annotations

from functools import lru_cache

from app.calendar.ephemeris.time_utils import to_nepal_time
from app.calendar.sankranti import get_sankrantis_in_year

from .models import SolarIngressEvent


@lru_cache(maxsize=512)
def gregorian_sankranti_events(gregorian_year: int) -> tuple[SolarIngressEvent, ...]:
    events: list[SolarIngressEvent] = []
    for row in get_sankrantis_in_year(gregorian_year):
        dt_utc = row["datetime_utc"]
        events.append(
            SolarIngressEvent(
                bs_month=int(row["bs_month_number"]),
                bs_month_name=str(row["bs_month"]),
                rashi_index=int(row["rashi_index"]),
                rashi_name=str(row["rashi_name"]),
                datetime_utc=dt_utc,
                datetime_nepal=to_nepal_time(dt_utc),
            )
        )
    return tuple(events)


def events_around_bs_year(bs_year: int) -> list[SolarIngressEvent]:
    gregorian_year = bs_year - 57
    events = [
        *gregorian_sankranti_events(gregorian_year),
        *gregorian_sankranti_events(gregorian_year + 1),
    ]
    return sorted(events, key=lambda event: event.datetime_utc)
