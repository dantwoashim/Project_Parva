"""Forecast endpoint contract checks (Year 3 Week 13-16)."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_forecast_festivals_contract_shape():
    response = client.get("/api/forecast/festivals", params={"year": 2050})
    assert response.status_code == 200
    body = response.json()

    assert body["year"] == 2050
    assert isinstance(body["count"], int)
    assert isinstance(body["festivals"], list)
    assert "note" in body
    if body["festivals"]:
        row = body["festivals"][0]
        assert {"festival_id", "start_date", "end_date", "horizon_years", "estimated_accuracy"} <= set(row.keys())
        assert 0 <= row["estimated_accuracy"] <= 1
        assert row["confidence_interval_days"] >= 0


def test_forecast_error_curve_contract_shape():
    response = client.get(
        "/api/forecast/error-curve",
        params={"start_year": 2030, "end_year": 2035},
    )
    assert response.status_code == 200
    body = response.json()

    assert body["start_year"] == 2030
    assert body["end_year"] == 2035
    assert len(body["points"]) == 6
    assert body["points"][0]["year"] == 2030
    assert 0 <= body["points"][0]["estimated_accuracy"] <= 1


def test_forecast_v2_alias_available():
    old_resp = client.get("/api/forecast/festivals", params={"year": 2040})
    new_resp = client.get("/v3/api/forecast/festivals", params={"year": 2040})
    assert old_resp.status_code == 200
    assert new_resp.status_code == 200
    assert old_resp.json()["year"] == new_resp.json()["year"] == 2040
