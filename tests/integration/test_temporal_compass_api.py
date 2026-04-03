from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_temporal_compass_post_supported_for_private_inputs():
    response = client.post(
        "/v3/api/temporal/compass",
        json={"date": "2026-02-15", "lat": "27.7172", "lon": "85.3240"},
    )

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    body = response.json()
    assert "primary_readout" in body
    assert body["method_profile"] == "temporal_compass_v1"
    assert body["engine_path"] == "ephemeris_udaya"
    assert body["fallback_used"] is False
    assert body["calibration_status"] == "unavailable"
    assert body["risk_mode"] == "standard"
    assert body["boundary_radar"] in {"stable", "one_day_sensitive", "high_disagreement_risk"}
    assert isinstance(body["stability_score"], float)
    assert body["recommended_action"]


def test_temporal_compass_post_accepts_numeric_coordinates():
    response = client.post(
        "/v3/api/temporal/compass",
        json={"date": "2026-02-15", "lat": 27.7172, "lon": 85.3240},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["primary_readout"]["tithi_name"]


def test_temporal_compass_get_and_post_normalize_coordinates_equivalently():
    params = {"date": "2026-02-15", "lat": "27.7172", "lon": "85.3240"}
    payload = {"date": "2026-02-15", "lat": 27.7172, "lon": 85.3240}

    get_response = client.get("/v3/api/temporal/compass", params=params)
    post_response = client.post("/v3/api/temporal/compass", json=payload)

    assert get_response.status_code == 200
    assert post_response.status_code == 200

    get_body = get_response.json()
    post_body = post_response.json()

    assert get_body["primary_readout"] == post_body["primary_readout"]
    assert get_body["signals"] == post_body["signals"]
    assert get_body["today"] == post_body["today"]


def test_temporal_compass_invalid_coordinates_return_400():
    get_response = client.get(
        "/v3/api/temporal/compass",
        params={"date": "2026-02-15", "lat": "999", "lon": "85.3240"},
    )
    post_response = client.post(
        "/v3/api/temporal/compass",
        json={"date": "2026-02-15", "lat": 999, "lon": 85.3240},
    )

    assert get_response.status_code == 400
    assert post_response.status_code == 400
    assert "Out-of-range lat" in get_response.json()["detail"]
    assert "Out-of-range lat" in post_response.json()["detail"]
