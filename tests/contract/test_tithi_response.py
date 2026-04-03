"""Contract tests for /api/calendar/tithi metadata (Week 15)."""

from app.main import app
from fastapi.testclient import TestClient


def test_calendar_tithi_endpoint_contract():
    client = TestClient(app)
    response = client.get("/api/calendar/tithi", params={"date": "2026-02-15"})
    assert response.status_code == 200

    body = response.json()
    assert body["engine_version"] == "v3"
    assert body["support_tier"] in {"computed", "heuristic"}
    assert body["engine_path"] in {"ephemeris_udaya", "instantaneous"}
    assert isinstance(body["fallback_used"], bool)
    assert body["calibration_status"] == "unavailable"
    assert body["boundary_radar"] in {"stable", "one_day_sensitive", "high_disagreement_risk"}
    assert body["risk_mode"] == "standard"
    assert isinstance(body["stability_score"], float)
    assert isinstance(body["abstained"], bool)
    assert body["recommended_action"]
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

    body = response.json()
    assert body["support_tier"] in {"computed", "estimated", "heuristic"}
    assert body["engine_path"] in {"ephemeris_udaya", "instantaneous"}
    assert isinstance(body["fallback_used"], bool)
    assert body["calibration_status"] == "unavailable"
    assert body["boundary_radar"] in {"stable", "one_day_sensitive", "high_disagreement_risk"}
    assert body["risk_mode"] == "standard"
    assert isinstance(body["stability_score"], float)
    assert isinstance(body["abstained"], bool)
    assert body["recommended_action"]

    t = body["tithi"]
    assert "method" in t
    assert "confidence" in t
    assert "reference_time" in t
    assert "sunrise_used" in t


def test_calendar_panchanga_has_tithi_method_metadata():
    client = TestClient(app)
    response = client.get("/api/calendar/panchanga", params={"date": "2026-02-15"})
    assert response.status_code == 200

    body = response.json()
    assert body["support_tier"] in {"computed", "heuristic"}
    assert body["engine_path"] == "ephemeris_udaya"
    assert body["fallback_used"] is False
    assert body["calibration_status"] == "unavailable"
    assert body["boundary_radar"] in {"stable", "one_day_sensitive", "high_disagreement_risk"}
    assert body["risk_mode"] == "standard"
    assert isinstance(body["stability_score"], float)
    assert isinstance(body["abstained"], bool)
    assert body["recommended_action"]

    t = body["panchanga"]["tithi"]
    assert t["method"] == "ephemeris_udaya"
    assert t["reference_time"] == "sunrise"
    assert t["confidence"] == "exact"
