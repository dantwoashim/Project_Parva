from __future__ import annotations

from datetime import date

from app.bootstrap.app_factory import create_app
from fastapi.testclient import TestClient


def test_observance_stream_uses_single_window_batch(monkeypatch):
    monkeypatch.setenv("PARVA_RATE_LIMIT_ENABLED", "false")

    import app.api.observance_routes as observance_routes

    calls = []

    def fake_window(start: date, *, days: int, location: str, preferences: list[str] | None):
        calls.append((start, days, location, tuple(preferences or ())))
        return [
            {
                "date": (start).isoformat(),
                "observances": [
                    {
                        "rank": 1,
                        "observance": "fixture",
                        "calendar_family": "nepali_hindu",
                        "date": start.isoformat(),
                        "confidence": "computed",
                        "rank_score": 1,
                        "reason_codes": [],
                        "metadata": {},
                    }
                ],
            }
        ] * days

    monkeypatch.setattr(observance_routes, "resolve_observance_window", fake_window)
    client = TestClient(create_app())

    response = client.get("/v3/api/observances/stream?start=2026-10-21&days=7")

    assert response.status_code == 200
    assert len(response.json()["results"]) == 7
    assert calls == [(date(2026, 10, 21), 7, "kathmandu", ())]
