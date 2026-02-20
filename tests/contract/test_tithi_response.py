"""Contract tests for /api/calendar/tithi metadata (Week 15)."""

from fastapi.testclient import TestClient

from app.main import app


def test_calendar_tithi_endpoint_contract():
    client = TestClient(app)
    response = client.get("/api/calendar/tithi", params={"date": "2026-02-15"})
    assert response.status_code == 200

    body = response.json()
    assert body["engine_version"] == "v3"
    assert "tithi" in body
    t = body["tithi"]

    assert t["method"] in {"ephemeris_udaya", "instantaneous"}
    assert t["confidence"] in {"exact", "computed"}
    assert t["reference_time"] in {"sunrise", "instantaneous"}
    assert "vriddhi" in t
    assert "ksheepana" in t


def test_calendar_today_has_udaya_metadata_fields():
    client = TestClient(app)
    response = client.get("/api/calendar/today")
    assert response.status_code == 200

    t = response.json()["tithi"]
    assert "method" in t
    assert "confidence" in t
    assert "reference_time" in t
    assert "sunrise_used" in t


def test_calendar_panchanga_has_tithi_method_metadata():
    client = TestClient(app)
    response = client.get("/api/calendar/panchanga", params={"date": "2026-02-15"})
    assert response.status_code == 200

    t = response.json()["panchanga"]["tithi"]
    assert t["method"] == "ephemeris_udaya"
    assert t["reference_time"] == "sunrise"
    assert t["confidence"] == "exact"
