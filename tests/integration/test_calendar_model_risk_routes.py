"""Public-profile tests for the calendar model-risk route boundary."""

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_calendar_model_risk_capabilities_are_public_v5():
    response = client.get("/v5/api/calendar-model-risk/capabilities")

    assert response.status_code == 200
    body = response.json()
    assert body["surface"] == "future_bs_risk_research"
    assert body["status"] == "research_preview"
    assert body["maturity"] == "research_preview"
    assert body["publication_status"] == "computed_prediction_not_official"
    assert body["review_required"] is True
    assert body["claim_boundary"] == "research_preview_not_safe_for_legal_or_payroll_use"
    assert "computed_prediction_not_official" in body["warnings"]
    assert "aggregate_validation_posture" in body["public_surface"]
    assert "source_trust_levels" not in body
    assert "capabilities" not in body
    assert "official future" in body["not_authority"]


def test_calendar_model_risk_private_routes_are_not_public_in_default_profile():
    sensitive_gets = [
        "/v5/api/calendar-model-risk/prediction/2089/6",
        "/v5/api/calendar-model-risk/prediction-set/2089/6",
        "/v5/api/calendar-model-risk/committee-posterior/2089/6",
        "/v5/api/calendar-model-risk/perturbation-robustness/2089/6",
        "/v5/api/calendar-model-risk/red-team/2083-ashwin",
        "/v5/api/calendar-model-risk/claim-readiness",
        "/v5/api/calendar-model-risk/external-audit-readiness",
        "/v5/api/calendar-model-risk/reports/claim-readiness",
    ]

    for path in sensitive_gets:
        response = client.get(path)
        assert response.status_code == 404


def test_calendar_model_risk_private_post_routes_are_not_public_in_default_profile():
    sensitive_posts = [
        "/v5/api/calendar-model-risk/audit-external-sheet",
        "/v5/api/calendar-model-risk/calendar-var",
        "/v5/api/calendar-model-risk/stress-test",
    ]

    for path in sensitive_posts:
        response = client.post(path, json={})
        assert response.status_code == 404


def test_calendar_model_risk_private_routes_are_hidden_from_public_openapi():
    schema = client.get("/openapi.json").json()
    paths = set(schema["paths"])

    assert "/v5/api/calendar-model-risk/capabilities" in paths
    assert all(
        path not in paths
        for path in {
            "/v5/api/calendar-model-risk/prediction/{bs_year}/{month}",
            "/v5/api/calendar-model-risk/prediction-set/{bs_year}/{month}",
            "/v5/api/calendar-model-risk/committee-posterior/{bs_year}/{month}",
            "/v5/api/calendar-model-risk/perturbation-robustness/{bs_year}/{month}",
            "/v5/api/calendar-model-risk/audit-external-sheet",
            "/v5/api/calendar-model-risk/calendar-var",
            "/v5/api/calendar-model-risk/stress-test",
            "/v5/api/calendar-model-risk/red-team/2083-ashwin",
            "/v5/api/calendar-model-risk/claim-readiness",
            "/v5/api/calendar-model-risk/external-audit-readiness",
            "/v5/api/calendar-model-risk/reports/{report_id}",
        }
    )


def test_calendar_model_risk_private_routes_are_hidden_from_schema_when_mounted(monkeypatch):
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "full_dev")
    monkeypatch.setenv("PARVA_ENABLE_EXPERIMENTAL_API", "true")
    monkeypatch.setenv("PARVA_ENABLE_RESEARCH_API", "true")
    monkeypatch.setenv("PARVA_ADMIN_TOKEN", "test-token")
    monkeypatch.delenv("PARVA_SHOW_PRIVATE_SCHEMA", raising=False)

    from app.bootstrap.app_factory import create_app

    private_client = TestClient(create_app())

    assert private_client.get("/v5/api/calendar-model-risk/prediction/2089/6").status_code == 401
    paths = set(private_client.get("/openapi.json").json()["paths"])
    assert "/v5/api/calendar-model-risk/capabilities" in paths
    assert "/v5/api/calendar-model-risk/prediction/{bs_year}/{month}" not in paths


def test_calendar_model_risk_private_routes_require_research_api_flag(monkeypatch):
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "full_dev")
    monkeypatch.setenv("PARVA_ENABLE_EXPERIMENTAL_API", "true")
    monkeypatch.setenv("PARVA_ENABLE_RESEARCH_API", "false")
    monkeypatch.setenv("PARVA_ADMIN_TOKEN", "test-token")
    monkeypatch.setenv("PARVA_RATE_LIMIT_ENABLED", "false")

    from app.bootstrap.app_factory import create_app

    guarded_client = TestClient(create_app())

    assert guarded_client.get("/v5/api/calendar-model-risk/capabilities").status_code == 200
    response = guarded_client.get("/v5/api/calendar-model-risk/prediction/2089/6")
    assert response.status_code in {401, 404}
    paths = set(guarded_client.get("/openapi.json").json()["paths"])
    assert "/v5/api/calendar-model-risk/prediction/{bs_year}/{month}" not in paths
