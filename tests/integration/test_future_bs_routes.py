"""Public-profile tests for the Future BS route boundary."""

from __future__ import annotations

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_future_bs_capabilities_is_public_v4_without_experimental_flag():
    response = client.get("/v4/api/future-bs/capabilities")

    assert response.status_code == 200
    body = response.json()
    assert body["surface"] == "future_bs_risk_research"
    assert body["status"] == "research_preview"
    assert body["publication_status"] == "computed_prediction_not_official"
    assert "official_future_publication" in body["not_claimed"]
    assert "methodology_summary" in body["public_surface"]
    assert "model_registry" not in body
    assert "precomputed_store" not in body
    assert "solar_ingress_cache" not in body


def test_future_bs_private_routes_are_not_public_in_default_profile():
    sensitive_paths = [
        "/v4/api/future-bs/month-lengths/2085",
        "/v4/api/future-bs/month-lengths/range?start=2084&end=2085",
        "/v4/api/future-bs/month-lengths/export.csv?start=2084&end=2085",
        "/v4/api/future-bs/export.xlsx?start=2084&end=2085",
        "/v4/api/future-bs/backtest?mode=full&test_start=2076&test_end=2076",
        "/v4/api/future-bs/backtest/residuals?train_start=2040&train_end=2075&test_start=2076&test_end=2076",
        "/v4/api/future-bs/month-lengths/explain?year=2085&month=6",
        "/v4/api/future-bs/boundary-risk?year=2085&month=6",
        "/v4/api/future-bs/model-runs",
    ]

    for path in sensitive_paths:
        response = client.get(path)
        assert response.status_code == 404


def test_future_bs_private_post_routes_are_not_public_in_default_profile():
    sensitive_posts = [
        "/v4/api/future-bs/month-lengths/compare",
        "/v4/api/future-bs/month-lengths/import-excel",
        "/v4/api/future-bs/loan-impact/simulate",
    ]

    for path in sensitive_posts:
        response = client.post(path, json={})
        assert response.status_code == 404


def test_future_bs_private_routes_are_hidden_from_public_openapi():
    schema = client.get("/openapi.json").json()
    paths = set(schema["paths"])

    assert "/v4/api/future-bs/capabilities" in paths
    assert all(
        path not in paths
        for path in {
            "/v4/api/future-bs/month-lengths/{bs_year}",
            "/v4/api/future-bs/month-lengths/range",
            "/v4/api/future-bs/month-lengths/export.csv",
            "/v4/api/future-bs/export.csv",
            "/v4/api/future-bs/export.xlsx",
            "/v4/api/future-bs/month-lengths/explain",
            "/v4/api/future-bs/boundary-risk",
            "/v4/api/future-bs/backtest",
            "/v4/api/future-bs/backtest/residuals",
            "/v4/api/future-bs/model-runs",
            "/v4/api/future-bs/loan-impact/simulate",
            "/v4/api/future-bs/month-lengths/import-excel",
            "/v4/api/future-bs/month-lengths/compare",
        }
    )


def test_future_bs_private_routes_are_hidden_from_schema_when_mounted(monkeypatch):
    monkeypatch.setenv("PARVA_ENABLE_EXPERIMENTAL_API", "true")
    monkeypatch.setenv("PARVA_ADMIN_TOKEN", "test-token")
    monkeypatch.delenv("PARVA_SHOW_PRIVATE_SCHEMA", raising=False)

    from app.bootstrap.app_factory import create_app

    private_client = TestClient(create_app())

    assert private_client.get("/v4/api/future-bs/month-lengths/2085").status_code == 401
    paths = set(private_client.get("/openapi.json").json()["paths"])
    assert "/v4/api/future-bs/capabilities" in paths
    assert "/v4/api/future-bs/month-lengths/{bs_year}" not in paths


def test_public_demo_profile_only_exposes_demo_api_paths(monkeypatch):
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "public_demo")
    monkeypatch.setenv("PARVA_ENABLE_EXPERIMENTAL_API", "false")
    monkeypatch.setenv("PARVA_SHOW_PRIVATE_SCHEMA", "false")
    monkeypatch.setenv("PARVA_ENV", "public")
    monkeypatch.setenv("PARVA_SOURCE_URL", "https://github.com/dantwoashim/Project_Parva")
    monkeypatch.setenv("PARVA_RATE_LIMIT_ENABLED", "false")

    from app.bootstrap.app_factory import create_app

    public_demo_client = TestClient(create_app())
    paths = set(public_demo_client.get("/openapi.json").json()["paths"])

    assert "/v3/api/calendar/today" in paths
    assert "/v3/api/calendar/convert" in paths
    assert "/v3/api/calendar/bs-to-gregorian" in paths
    assert "/v4/api/future-bs/capabilities" in paths
    assert "/v4/api/future-bs/month-lengths/{bs_year}" not in paths
    assert "/v5/api/calendar-model-risk/capabilities" not in paths
    assert "/v3/api/enterprise/capabilities" not in paths
    assert "/v3/api/impact/simulate" not in paths
    assert "/v3/api/agent/capabilities" not in paths
    assert "/v3/api/protocol/version" not in paths

    assert public_demo_client.get("/v3/api/calendar/today").status_code == 200
    assert public_demo_client.get("/v4/api/future-bs/capabilities").status_code == 200
    assert public_demo_client.get("/v3/api/enterprise/capabilities").status_code == 404
    assert public_demo_client.get("/v3/api/agent/capabilities").status_code == 404
    assert public_demo_client.get("/v3/api/protocol/version").status_code == 404


def test_public_demo_blocks_unverified_future_bs_to_ad_by_default(monkeypatch):
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "public_demo")
    monkeypatch.setenv("PARVA_ENABLE_EXPERIMENTAL_API", "false")
    monkeypatch.setenv("PARVA_SHOW_PRIVATE_SCHEMA", "false")
    monkeypatch.setenv("PARVA_ENV", "public")
    monkeypatch.setenv("PARVA_SOURCE_URL", "https://github.com/dantwoashim/Project_Parva")
    monkeypatch.setenv("PARVA_RATE_LIMIT_ENABLED", "false")
    monkeypatch.delenv("PARVA_ALLOW_PUBLIC_UNVERIFIED_FUTURE_CONVERSION", raising=False)

    from app.bootstrap.app_factory import create_app

    public_demo_client = TestClient(create_app())

    verified = public_demo_client.post(
        "/v3/api/calendar/bs-to-gregorian",
        json={"year": 2083, "month": 1, "day": 1},
    )
    assert verified.status_code == 200

    blocked = public_demo_client.post(
        "/v3/api/calendar/bs-to-gregorian",
        json={"year": 2084, "month": 1, "day": 1},
    )
    assert blocked.status_code == 403
    body = blocked.json()
    text = str(body)
    assert "UNVERIFIED_FUTURE_BS_CONVERSION_BLOCKED" in text
    assert "computed_prediction_not_official" in text
    assert "gregorian" not in body


def test_public_unverified_future_bs_to_ad_requires_explicit_flag(monkeypatch):
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "public_demo")
    monkeypatch.setenv("PARVA_ENABLE_EXPERIMENTAL_API", "false")
    monkeypatch.setenv("PARVA_SHOW_PRIVATE_SCHEMA", "false")
    monkeypatch.setenv("PARVA_ENV", "public")
    monkeypatch.setenv("PARVA_SOURCE_URL", "https://github.com/dantwoashim/Project_Parva")
    monkeypatch.setenv("PARVA_RATE_LIMIT_ENABLED", "false")
    monkeypatch.setenv("PARVA_ALLOW_PUBLIC_UNVERIFIED_FUTURE_CONVERSION", "true")

    from app.bootstrap.app_factory import create_app

    public_demo_client = TestClient(create_app())
    response = public_demo_client.post(
        "/v3/api/calendar/bs-to-gregorian",
        json={"year": 2084, "month": 1, "day": 1},
    )
    assert response.status_code == 200
    assert response.json()["bs"]["confidence"] in {"static_lookup", "estimated"}
