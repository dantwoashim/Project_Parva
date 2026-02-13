"""Sunrise corpus regression tests (Week 13)."""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

from app.calendar.ephemeris.swiss_eph import LAT_KATHMANDU, LON_KATHMANDU, calculate_sunrise
from app.calendar.ephemeris.time_utils import to_nepal_time


FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "sunrise_kathmandu_50.json"


def test_sunrise_fixture_has_50_rows():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert data["metadata"]["samples"] == 50
    assert len(data["samples"]) == 50


def test_sunrise_matches_fixture_within_one_minute():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))

    for row in data["samples"]:
        d = date.fromisoformat(row["date"])
        expected = datetime.fromisoformat(row["sunrise_npt"])
        actual = to_nepal_time(calculate_sunrise(d, LAT_KATHMANDU, LON_KATHMANDU))

        delta_seconds = abs((actual - expected).total_seconds())
        assert delta_seconds <= 60
