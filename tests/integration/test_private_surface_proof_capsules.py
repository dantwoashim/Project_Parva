"""Integration tests for personal and temporal proof-capsule surfaces."""

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_temporal_compass_proof_capsule_post_hides_inputs_and_exposes_risk():
    response = client.post(
        "/v3/api/temporal/compass/proof-capsule",
        json={
            "date": "2026-02-15",
            "lat": 27.7172,
            "lon": 85.3240,
            "quality_band": "computed",
            "risk_mode": "strict",
        },
    )

    assert response.status_code == 200
    assert response.request.url.query == b""
    assert response.headers["Cache-Control"] == "no-store"
    body = response.json()
    assert body["surface"] == "temporal_compass"
    assert body["request"]["risk_mode"] == "strict"
    assert body["selection"]["engine_path"] == "ephemeris_udaya"
    assert body["risk"]["risk_mode"] == "strict"
    assert body["risk"]["boundary_radar"] in {"stable", "one_day_sensitive", "high_disagreement_risk"}
    assert isinstance(body["risk"]["truth_ladder"], list)


def test_personal_panchanga_proof_capsule_returns_private_lineage_sections():
    response = client.post(
        "/v3/api/personal/panchanga/proof-capsule",
        json={"date": "2026-02-15", "lat": 27.7172, "lon": 85.3240, "risk_mode": "strict"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["surface"] == "personal_panchanga"
    assert body["selection"]["engine_path"] == "ephemeris_udaya"
    assert body["selection"]["support_tier"] in {"computed", "heuristic", "estimated"}
    assert body["source_lineage"]["timezone_source"] in {"user_input", "default_kathmandu"}
    assert body["source_lineage"]["input_sources"]["latitude"] == "user_input"
    assert body["risk"]["risk_mode"] == "strict"
    assert body["calculation_trace_id"]


def test_personal_context_proof_capsule_carries_reminder_lineage():
    response = client.post(
        "/v3/api/personal/context/proof-capsule",
        json={"date": "2026-02-15", "risk_mode": "strict"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["surface"] == "personal_context"
    assert body["selection"]["engine_path"] == "personal_context_synthesis"
    assert isinstance(body["source_lineage"]["upcoming_reminder_count"], int)
    assert body["risk"]["boundary_radar"] in {"stable", "one_day_sensitive", "high_disagreement_risk"}
    assert isinstance(body["risk"]["truth_ladder"], list)
