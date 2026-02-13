from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_convert_includes_uncertainty_fields():
    resp = client.get("/v2/api/calendar/convert", params={"date": "2026-02-15"})
    assert resp.status_code == 200
    body = resp.json()

    assert "uncertainty" in body["bikram_sambat"]
    assert "level" in body["bikram_sambat"]["uncertainty"]
    assert "uncertainty" in body["tithi"]
    assert "probability" in body["tithi"]["uncertainty"]


def test_tithi_endpoint_includes_uncertainty_object():
    resp = client.get("/v2/api/calendar/tithi", params={"date": "2026-02-15"})
    assert resp.status_code == 200
    body = resp.json()
    assert "uncertainty" in body["tithi"]
    assert "interval_hours" in body["tithi"]["uncertainty"]


def test_panchanga_includes_astronomical_uncertainty():
    resp = client.get("/v2/api/calendar/panchanga", params={"date": "2026-02-15"})
    assert resp.status_code == 200
    body = resp.json()
    assert "uncertainty" in body["panchanga"]
    assert body["panchanga"]["uncertainty"]["methodology"] == "ephemeris_panchanga"
