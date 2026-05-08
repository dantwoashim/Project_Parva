"""Solar-ingress cache tests."""

from __future__ import annotations

from pathlib import Path

from app.future_bs.solar_ingress_cache import (
    cached_events_for_gregorian_year,
    load_solar_ingress_cache,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SAMPLE_CACHE = PROJECT_ROOT / "data" / "future_bs" / "astronomy" / "solar_ingress_events_sample.json"


def test_solar_ingress_public_sample_loads_de440_events():
    payload = load_solar_ingress_cache(SAMPLE_CACHE)

    assert payload["available"] is True
    assert payload["ephemeris"] == "jpl_de440"
    assert sorted(payload["years"]) == [2027]


def test_cached_year_uses_configured_private_cache_path(monkeypatch):
    from app.future_bs import solar_ingress_cache

    monkeypatch.setattr(solar_ingress_cache, "DEFAULT_EVENTS_PATH", SAMPLE_CACHE)
    solar_ingress_cache.load_solar_ingress_cache.cache_clear()
    events = cached_events_for_gregorian_year(2027, ephemeris_label="jpl_de440")

    solar_ingress_cache.load_solar_ingress_cache.cache_clear()
    assert events is not None
    assert len(events) == 12
    assert all(event.ephemeris == "jpl_de440" for event in events)


def test_trusted_sample_can_serve_readonly_when_live_ephemeris_is_swiss(monkeypatch):
    from app.future_bs import solar_ingress_cache

    monkeypatch.setattr(solar_ingress_cache, "DEFAULT_EVENTS_PATH", SAMPLE_CACHE)
    solar_ingress_cache.load_solar_ingress_cache.cache_clear()
    events = cached_events_for_gregorian_year(2027, ephemeris_label="swiss_moshier")

    solar_ingress_cache.load_solar_ingress_cache.cache_clear()
    assert events is not None
    assert len(events) == 12
