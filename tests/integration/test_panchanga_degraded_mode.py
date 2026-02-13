"""Reliability degraded-mode behavior for panchanga endpoint."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_panchanga_returns_503_when_engine_fails_and_no_cache(monkeypatch):
    import app.calendar.panchanga as panchanga_module
    import app.cache.precomputed as precomputed_module

    monkeypatch.setattr(precomputed_module, "PRECOMPUTE_DIR", precomputed_module.PRECOMPUTE_DIR / "missing_test_dir")

    def _boom(_):
        raise RuntimeError("ephemeris unavailable")

    monkeypatch.setattr(panchanga_module, "get_panchanga", _boom)

    client = TestClient(app)
    response = client.get("/api/calendar/panchanga", params={"date": "1999-01-01"})
    assert response.status_code == 503
    assert "Panchanga engine unavailable" in response.json()["detail"]
