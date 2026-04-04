"""Integration tests for calendar proof-capsule surfaces."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_today_proof_capsule_returns_portable_risk_sections():
    response = client.get("/api/calendar/today/proof-capsule", params={"risk_mode": "strict"})
    assert response.status_code == 200

    body = response.json()
    assert body["surface"] == "today"
    assert body["request"]["risk_mode"] == "strict"
    assert body["selection"]["engine_path"] in {"ephemeris_udaya", "instantaneous"}
    assert body["selection"]["support_tier"] in {"computed", "heuristic", "estimated"}
    assert body["risk"]["boundary_radar"] in {"stable", "one_day_sensitive", "high_disagreement_risk"}
    assert body["risk"]["risk_mode"] == "strict"
    assert isinstance(body["risk"]["truth_ladder"], list)


def test_tithi_proof_capsule_returns_request_and_lineage():
    response = client.get(
        "/api/calendar/tithi/proof-capsule",
        params={"date": "2026-02-15", "latitude": 27.7172, "longitude": 85.3240, "risk_mode": "strict"},
    )
    assert response.status_code == 200

    body = response.json()
    assert body["surface"] == "tithi"
    assert body["request"]["date"] == "2026-02-15"
    assert body["source_lineage"]["method"] in {"ephemeris_udaya", "instantaneous"}
    assert body["source_lineage"]["reference_time"] in {"sunrise", "instantaneous"}
    assert body["risk"]["risk_mode"] == "strict"
    assert body["provenance"]


def test_panchanga_proof_capsule_returns_cache_and_risk_context():
    response = client.get(
        "/api/calendar/panchanga/proof-capsule",
        params={"date": "2026-02-15", "risk_mode": "strict"},
    )
    assert response.status_code == 200

    body = response.json()
    assert body["surface"] == "panchanga"
    assert body["request"]["date"] == "2026-02-15"
    assert body["selection"]["engine_path"] == "ephemeris_udaya"
    assert body["source_lineage"]["cache"]["source"] in {"computed", "precomputed"}
    assert body["risk"]["boundary_radar"] in {"stable", "one_day_sensitive", "high_disagreement_risk"}
    assert isinstance(body["risk"]["truth_ladder"], list)
