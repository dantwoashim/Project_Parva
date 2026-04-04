"""Integration tests for request guard middleware."""

from __future__ import annotations

import pytest
from app.bootstrap.app_factory import create_app
from fastapi.testclient import TestClient


def _client():
    return TestClient(create_app())


def test_rejects_oversized_query_string():
    long_query = "a" * 5000
    response = _client().get(f"/api/calendar/convert?date=2026-02-15&x={long_query}")
    assert response.status_code == 414
    assert response.json()["detail"] == "Query string too long"


def test_rejects_oversized_payload():
    # Force large content length with raw payload header
    huge = ("x" * (2 * 1024 * 1024)).encode("utf-8")
    response = _client().post(
        "/api/placeholder",
        content=huge,
        headers={"Content-Type": "application/json", "Content-Length": str(len(huge))},
    )
    assert response.status_code == 413
    assert response.json()["detail"] == "Request payload too large"


def test_rejects_invalid_content_length_header():
    response = _client().post(
        "/api/personal/panchanga",
        content=b'{"date":"2026-02-15"}',
        headers={"Content-Type": "application/json", "Content-Length": "not-a-number"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid content-length header"


def test_private_compute_routes_return_no_store_headers():
    response = _client().post("/api/personal/panchanga", json={"date": "2026-02-15"})
    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    assert response.headers["Pragma"] == "no-cache"


def test_common_headers_include_agpl_license():
    response = _client().get("/api/calendar/today")

    assert response.status_code == 200
    assert response.headers["X-Parva-License"] == "AGPL-3.0-or-later"


def test_source_endpoint_redirects_when_configured(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PARVA_SOURCE_URL", "https://example.com/source")
    client = TestClient(create_app())

    response = client.get("/source", follow_redirects=False)

    assert response.status_code in {302, 307}
    assert response.headers["location"] == "https://example.com/source"


def test_health_reports_source_metadata(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PARVA_SOURCE_URL", "https://example.com/source")
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["license"] == "AGPL-3.0-or-later"
    assert payload["source_code_url"] == "https://example.com/source"
