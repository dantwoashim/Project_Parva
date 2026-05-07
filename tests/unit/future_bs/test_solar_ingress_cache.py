"""Solar-ingress cache tests."""

from __future__ import annotations

from pathlib import Path

from app.future_bs.solar_ingress_cache import (
    cached_events_for_gregorian_year,
    solar_ingress_cache_status,
)


def test_solar_ingress_cache_loads_de440_events():
    status = solar_ingress_cache_status()

    assert status["available"] is True
    assert status["ephemeris"] == "jpl_de440"
    assert status["year_count"] >= 300


def test_cached_year_returns_twelve_events():
    events = cached_events_for_gregorian_year(2027, ephemeris_label="jpl_de440")

    assert events is not None
    assert len(events) == 12
    assert all(event.ephemeris == "jpl_de440" for event in events)


def test_parquet_cache_artifact_exists():
    assert Path("data/future_bs/astronomy/solar_ingress_events_1900_2200.parquet").exists()
