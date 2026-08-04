from __future__ import annotations

from app.bootstrap.app_factory import create_app
from fastapi.testclient import TestClient

PUBLIC_FRONTEND_ENDPOINTS = [
    "/health/ready",
    "/v3/api/calendar/today",
    "/v3/api/festivals",
    "/v3/api/feeds/next",
    "/v3/api/policy",
    "/v3/api/trust/capabilities",
    "/v3/api/timegraph/capabilities",
    "/v3/api/rules/capabilities",
    "/v3/api/impact/capabilities",
    "/v3/api/agent/capabilities",
    "/v3/api/protocol/version",
    "/v4/api/future-bs/capabilities",
    "/v4/api/future-bs/methodology",
    "/v4/api/future-bs/forecast/2084",
]


def test_developer_preview_profile_exposes_frontend_advertised_public_endpoints(monkeypatch):
    monkeypatch.setenv("PARVA_ENV", "test")
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "developer_preview")
    monkeypatch.setenv("PARVA_ENABLE_EXPERIMENTAL_API", "false")
    monkeypatch.setenv("PARVA_SHOW_PRIVATE_SCHEMA", "false")
    monkeypatch.setenv("PARVA_RATE_LIMIT_ENABLED", "false")

    client = TestClient(create_app())

    statuses = {path: client.get(path).status_code for path in PUBLIC_FRONTEND_ENDPOINTS}
    assert statuses == {path: 200 for path in PUBLIC_FRONTEND_ENDPOINTS}
