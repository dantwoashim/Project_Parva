"""Sankranti event accessors for future BS model diagnostics."""

from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache

from .ephemeris import MoshierAdapter
from .solar_ingress_solver import TARGET_LONGITUDES, SolarIngressSolution, solve_solar_ingress


@lru_cache(maxsize=256)
def solve_sankranti_events_for_gregorian_year(year: int) -> tuple[SolarIngressSolution, ...]:
    events: list[SolarIngressSolution] = []
    for index, longitude in enumerate(TARGET_LONGITUDES):
        rough_month = ((index + 3) % 12) + 1
        search_year = year if rough_month >= 4 else year + 1
        search_start = datetime(search_year, rough_month, 1, tzinfo=timezone.utc)
        events.append(
            solve_solar_ingress(
                longitude,
                search_start,
                adapter=MoshierAdapter(),
                ayanamsha="lahiri",
            )
        )
    return tuple(sorted(events, key=lambda event: event.utc_time))
