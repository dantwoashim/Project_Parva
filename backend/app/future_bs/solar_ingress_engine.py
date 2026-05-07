"""Solar-ingress event extraction for BS month boundaries."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from app.calendar.ephemeris.time_utils import to_nepal_time
from app.calendar.sankranti import get_sankrantis_in_year

from .ephemeris import JPLDe440Adapter
from .models import SolarIngressEvent
from .solar_ingress_solver import TARGET_LONGITUDES, solve_solar_ingress


def active_ephemeris_key() -> str:
    jpl = JPLDe440Adapter()
    if jpl.available:
        return f"jpl_de440:{jpl.kernel_path}"
    return "swiss_moshier_shared_sankranti"


def active_ephemeris_label() -> Literal["jpl_de440", "swiss_moshier"]:
    return "jpl_de440" if JPLDe440Adapter().available else "swiss_moshier"


@lru_cache(maxsize=512)
def _gregorian_sankranti_events(
    gregorian_year: int,
    ephemeris_key: str,
) -> tuple[SolarIngressEvent, ...]:
    jpl = JPLDe440Adapter()
    if ephemeris_key.startswith("jpl_de440") and jpl.available:
        return _jpl_gregorian_sankranti_events(gregorian_year, jpl)

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
                ephemeris="swiss_moshier",
                calculation_version="shared_sankranti_engine_v1",
            )
        )
    return tuple(events)


def _jpl_gregorian_sankranti_events(
    gregorian_year: int,
    adapter: JPLDe440Adapter,
) -> tuple[SolarIngressEvent, ...]:
    from datetime import datetime, timezone

    events: list[SolarIngressEvent] = []
    for index, longitude in enumerate(TARGET_LONGITUDES):
        rough_month = ((index + 3) % 12) + 1
        search_year = gregorian_year if rough_month >= 4 else gregorian_year + 1
        search_start = datetime(search_year, rough_month, 1, tzinfo=timezone.utc)
        solution = solve_solar_ingress(
            longitude,
            search_start,
            adapter=adapter,
            ayanamsha="lahiri",
        )
        events.append(
            SolarIngressEvent(
                bs_month=solution.bs_month,
                bs_month_name=solution.bs_month_name,
                rashi_index=solution.bs_month - 1,
                rashi_name=solution.sign,
                datetime_utc=solution.utc_time,
                datetime_nepal=solution.nepal_time,
                ephemeris=solution.ephemeris,
                calculation_version=solution.calculation_version,
            )
        )
    return tuple(sorted(events, key=lambda event: event.datetime_utc))


def gregorian_sankranti_events(gregorian_year: int) -> tuple[SolarIngressEvent, ...]:
    return _gregorian_sankranti_events(gregorian_year, active_ephemeris_key())


def events_around_bs_year(bs_year: int) -> list[SolarIngressEvent]:
    gregorian_year = bs_year - 57
    events = [
        *gregorian_sankranti_events(gregorian_year),
        *gregorian_sankranti_events(gregorian_year + 1),
    ]
    return sorted(events, key=lambda event: event.datetime_utc)
