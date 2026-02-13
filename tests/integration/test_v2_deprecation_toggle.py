"""Integration tests for optional v2 hard-deprecation gate."""

from fastapi.testclient import TestClient

from app.main import app


def test_v2_remains_available_by_default(monkeypatch):
    monkeypatch.delenv("PARVA_DISABLE_V2", raising=False)
    client = TestClient(app)
    response = client.get("/v2/api/calendar/today")
    assert response.status_code == 200


def test_v2_can_be_hard_disabled(monkeypatch):
    monkeypatch.setenv("PARVA_DISABLE_V2", "true")
    client = TestClient(app)
    response = client.get("/v2/api/calendar/today")
    assert response.status_code == 410
    body = response.json()
    assert "migration_guide" in body
    assert body["successor_version"] == "/v3/docs"
