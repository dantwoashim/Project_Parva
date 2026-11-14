"""Regression corpora ported from the legacy platform: published sunrises, sidereal ephemeris, official month table."""

import csv
import json
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from parva import bs

FIXTURES = Path(__file__).parent / "fixtures"
MONTH_KEYS = [n.lower() for n in bs.NAMES]


def test_sunrise_kathmandu_50() -> None:
    astro = pytest.importorskip("parva.astro")
    samples = json.loads((FIXTURES / "sunrise_kathmandu_50.json").read_text("utf-8"))["samples"]
    worst = 0.0
    for s in samples:
        got = astro.sunrise(date.fromisoformat(s["date"]), astro.KATHMANDU)
        want = datetime.fromisoformat(s["sunrise_utc"])
        worst = max(worst, abs((got - want).total_seconds()))
    assert worst < 60, f"max sunrise delta {worst:.1f}s"


def test_ephemeris_500_sidereal_lahiri() -> None:
    astro = pytest.importorskip("parva.astro")
    samples = json.loads((FIXTURES / "ephemeris_500.json").read_text("utf-8"))["samples"]
    worst_sun = worst_moon = 0.0
    for s in samples:
        sun, moon = astro.longitudes(datetime.fromisoformat(s["datetime_utc"]))
        worst_sun = max(worst_sun, abs((sun - s["sun_longitude"] + 180) % 360 - 180))
        worst_moon = max(worst_moon, abs((moon - s["moon_longitude"] + 180) % 360 - 180))
    assert worst_sun < 0.01 and worst_moon < 0.01, f"max deltas sun={worst_sun} moon={worst_moon}"


def test_official_holdout_month_lengths() -> None:
    rows = list(csv.DictReader((FIXTURES / "official_holdout_2078_2083.csv").open(encoding="utf-8")))
    for row in rows:
        year = int(row["bs_year"])
        for i, name in enumerate(MONTH_KEYS, start=1):
            assert bs.month_days(year, i) == int(row[name]), (year, name)


def test_sunrise_is_used_at_the_same_instant_as_tithi() -> None:
    pytest.importorskip("swisseph")
    from parva import astro, lunar

    p = lunar.panchanga(date(2026, 10, 11))
    rise = datetime.fromisoformat(p["sunrise"])
    assert astro.tithi(rise) == p["tithi"] and rise.utcoffset() == timedelta(hours=5, minutes=45)
