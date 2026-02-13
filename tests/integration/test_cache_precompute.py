"""Integration tests for precompute/cache serving paths (Year 3 Week 17-20)."""

from __future__ import annotations

import json
from datetime import date

from fastapi.testclient import TestClient

from app.main import app


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_panchanga_endpoint_uses_precomputed_cache(monkeypatch, tmp_path):
    import app.cache.precomputed as precomputed_module

    monkeypatch.setattr(precomputed_module, "PRECOMPUTE_DIR", tmp_path)

    target = date(2028, 6, 1)
    payload = {
        "year": 2028,
        "generated_at": "2028-01-01T00:00:00+00:00",
        "count": 1,
        "dates": {
            target.isoformat(): {
                "date": target.isoformat(),
                "bikram_sambat": {
                    "year": 2085,
                    "month": 2,
                    "day": 18,
                    "month_name": "Jestha",
                    "confidence": "official",
                    "source_range": "2000-2090",
                    "estimated_error_days": None,
                    "uncertainty": {"level": "exact"},
                },
                "panchanga": {
                    "confidence": "astronomical",
                    "uncertainty": {"level": "exact"},
                    "tithi": {"number": 1, "name": "Pratipada", "paksha": "shukla", "progress": 0.1},
                    "nakshatra": {"number": 1, "name": "Ashwini", "pada": 1},
                    "yoga": {"number": 1, "name": "Vishkumbha"},
                    "karana": {"number": 1, "name": "Kimstughna"},
                    "vaara": {"name_sanskrit": "Ravivara", "name_english": "Sunday"},
                },
                "ephemeris": {"mode": "swiss_moshier", "accuracy": "arcsecond", "library": "pyswisseph"},
            }
        },
    }
    _write_json(tmp_path / "panchanga_2028.json", payload)

    client = TestClient(app)
    response = client.get("/api/calendar/panchanga", params={"date": target.isoformat()})
    assert response.status_code == 200
    body = response.json()
    assert body["cache"]["hit"] is True
    assert body["cache"]["source"] == "precomputed"
    assert body["panchanga"]["tithi"]["name"] == "Pratipada"


def test_upcoming_festivals_uses_precomputed_cache(monkeypatch, tmp_path):
    import app.cache.precomputed as precomputed_module
    import app.calendar.routes as calendar_routes

    class FakeDate(date):
        @classmethod
        def today(cls):
            return cls(2028, 1, 1)

    monkeypatch.setattr(precomputed_module, "PRECOMPUTE_DIR", tmp_path)
    monkeypatch.setattr(calendar_routes, "date", FakeDate)

    _write_json(
        tmp_path / "festivals_2028.json",
        {
            "year": 2028,
            "generated_at": "2028-01-01T00:00:00+00:00",
            "count": 1,
            "festivals": [
                {
                    "festival_id": "demo-festival",
                    "start": "2028-01-10",
                    "end": "2028-01-10",
                    "duration_days": 1,
                    "method": "fixed",
                }
            ],
        },
    )

    client = TestClient(app)
    response = client.get("/api/calendar/festivals/upcoming", params={"days": 20})
    assert response.status_code == 200
    body = response.json()
    assert body["cache"]["hit"] is True
    assert body["festivals"][0]["festival_id"] == "demo-festival"


def test_cache_stats_endpoint_lists_available_years(monkeypatch, tmp_path):
    import app.cache.precomputed as precomputed_module

    monkeypatch.setattr(precomputed_module, "PRECOMPUTE_DIR", tmp_path)
    _write_json(tmp_path / "panchanga_2028.json", {"dates": {}})
    _write_json(tmp_path / "festivals_2028.json", {"festivals": []})

    client = TestClient(app)
    response = client.get("/api/cache/stats")
    assert response.status_code == 200
    body = response.json()
    assert 2028 in body["years"]["panchanga"]
    assert 2028 in body["years"]["festivals"]
