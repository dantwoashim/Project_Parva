"""500-timestamp ephemeris verification (Week 11)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from app.calendar.ephemeris.swiss_eph import get_sun_moon_positions


FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "ephemeris_500.json"


def test_ephemeris_fixture_has_500_samples():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert data["metadata"]["samples"] == 500
    assert len(data["samples"]) == 500


def test_sun_moon_positions_against_fixture_tolerance():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))

    # Tolerance aligned with weekly plan target.
    sun_tol = 0.01
    moon_tol = 0.05

    for row in data["samples"]:
        dt = datetime.fromisoformat(row["datetime_utc"])
        sun, moon = get_sun_moon_positions(dt)

        assert abs(sun - row["sun_longitude"]) <= sun_tol
        assert abs(moon - row["moon_longitude"]) <= moon_tol
