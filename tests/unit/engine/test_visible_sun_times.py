from __future__ import annotations

from datetime import date

from app.calendar.ephemeris.swiss_eph import (
    LAT_KATHMANDU,
    LON_KATHMANDU,
    calculate_sunrise,
    calculate_sunset,
)
from app.calendar.ephemeris.time_utils import to_nepal_time


def test_visible_limb_sun_times_match_public_reference_for_kathmandu():
    target_date = date(2026, 4, 4)

    sunrise = to_nepal_time(calculate_sunrise(target_date, LAT_KATHMANDU, LON_KATHMANDU))
    sunset = to_nepal_time(calculate_sunset(target_date, LAT_KATHMANDU, LON_KATHMANDU))

    assert sunrise.strftime("%H:%M") == "05:51"
    assert sunset.strftime("%H:%M") == "18:22"
