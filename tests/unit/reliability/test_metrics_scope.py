from __future__ import annotations

from app.bootstrap.app_factory import create_app
from fastapi.testclient import TestClient


def test_reliability_metrics_exposes_request_and_cache_scope(monkeypatch):
    monkeypatch.setenv("PARVA_RATE_LIMIT_ENABLED", "false")
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "developer_preview")
    client = TestClient(create_app())

    client.get("/v3/api/calendar/convert?date=2026-04-14")
    response = client.get("/v3/api/reliability/metrics")

    assert response.status_code == 200
    payload = response.json()
    assert "metrics" in payload
    assert "endpoints" in payload["metrics"]
    assert "cache" in payload["metrics"]
    assert any(row["path"] == "/v3/api/calendar/convert" for row in payload["metrics"]["endpoints"])
