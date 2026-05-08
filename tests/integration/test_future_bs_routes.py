"""Public-profile tests for the Future BS route boundary."""

from __future__ import annotations

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_future_bs_capabilities_is_public_v4_without_experimental_flag():
    response = client.get("/v4/api/future-bs/capabilities")

    assert response.status_code == 200
    body = response.json()
    assert body["surface"] == "future_bs_month_length_validation"
    assert body["status"] == "evaluation_ready"
    assert "official_future_publication" in body["not_claimed"]


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
