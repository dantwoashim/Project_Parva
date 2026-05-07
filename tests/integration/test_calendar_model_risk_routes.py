"""Integration tests for the calendar model-risk API."""

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_calendar_model_risk_capabilities_are_public_v5():
    response = client.get("/v5/api/calendar-model-risk/capabilities")

    assert response.status_code == 200
    body = response.json()
    assert body["surface"] == "calendar_model_risk"
    assert "calendar_var" in body["capabilities"]
    assert body["publication_status"] == "computed_prediction_not_official"


def test_calendar_model_risk_prediction_shape():
    response = client.get("/v5/api/calendar-model-risk/prediction/2089/6")

    assert response.status_code == 200
    body = response.json()
    assert body["bs_year"] == 2089
    assert body["month"] == "ashwin"
    assert body["predicted_days"] in {29, 30, 31, 32}
    assert body["prediction_set_95"]
    assert body["metadata"]["publication_status"] == "computed_prediction_not_official"
    assert body["committee_model"]["committee_rule_posterior"]
    assert "flip_rate" in body["perturbation_robustness"]


def test_calendar_var_and_claim_readiness_routes():
    var = client.post(
        "/v5/api/calendar-model-risk/calendar-var",
        json={
            "bs_year": 2089,
            "month": 6,
            "principal": 1_000_000,
            "annual_rate": 12,
            "affected_contracts": 10,
        },
    )
    assert var.status_code == 200
    assert var.json()["publication_status"] == "computed_prediction_not_official"
    assert var.json()["recommended_policy"]

    readiness = client.get("/v5/api/calendar-model-risk/claim-readiness")
    assert readiness.status_code == 200
    assert readiness.json()["ready_for_blanket_99_percent_claim"] is False


def test_2083_ashwin_red_team_route():
    response = client.get("/v5/api/calendar-model-risk/red-team/2083-ashwin")

    assert response.status_code == 200
    body = response.json()
    assert body["case_id"] == "PARVA-REDTEAM-2083-ASHWIN"
    assert body["publication_status"] == "computed_prediction_not_official"
