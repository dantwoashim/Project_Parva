from __future__ import annotations

import pytest
from app.bootstrap.app_factory import create_app
from fastapi.testclient import TestClient


def test_security_headers_include_csp(monkeypatch):
    monkeypatch.setenv("PARVA_RATE_LIMIT_ENABLED", "false")
    client = TestClient(create_app())

    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
    assert "https://cdn.jsdelivr.net" not in response.headers["Content-Security-Policy"]


def test_api_docs_csp_allows_swagger_assets(monkeypatch):
    monkeypatch.setenv("PARVA_RATE_LIMIT_ENABLED", "false")
    client = TestClient(create_app())

    response = client.get("/docs")

    assert response.status_code == 200
    assert "https://cdn.jsdelivr.net" in response.text
    csp = response.headers["Content-Security-Policy"]
    assert "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net" in csp
    assert "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net" in csp
    assert "frame-ancestors 'none'" in csp


def test_cors_preflight_uses_explicit_methods_and_headers(monkeypatch):
    monkeypatch.setenv("PARVA_RATE_LIMIT_ENABLED", "false")
    monkeypatch.setenv("CORS_ALLOW_ORIGINS", "https://example.com")
    client = TestClient(create_app())

    response = client.options(
        "/v3/api/calendar/today",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-API-Key",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-methods"] != "*"
    assert response.headers["access-control-allow-headers"] != "*"
    assert "GET" in response.headers["access-control-allow-methods"]
    assert "X-API-Key" in response.headers["access-control-allow-headers"]


def test_production_rejects_localhost_cors_origins(monkeypatch):
    monkeypatch.setenv("PARVA_ENV", "production")
    monkeypatch.setenv("PARVA_SOURCE_URL", "https://example.com/source")
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "public_reference")
    monkeypatch.setenv("PARVA_RATE_LIMIT_BACKEND", "redis")
    monkeypatch.setenv("PARVA_REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("PARVA_REQUIRE_PRECOMPUTED", "false")
    monkeypatch.setenv("PARVA_PROVENANCE_ATTESTATION_KEY", "test-provenance-key")
    monkeypatch.setenv("CORS_ALLOW_ORIGINS", "http://localhost:5173")

    with pytest.raises(RuntimeError, match="internet-exposed CORS origins cannot include localhost"):
        create_app()
