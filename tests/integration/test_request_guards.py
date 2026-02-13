"""Integration tests for request guard middleware."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_rejects_oversized_query_string():
    long_query = "a" * 5000
    response = client.get(f"/api/calendar/convert?date=2026-02-15&x={long_query}")
    assert response.status_code == 414
    assert response.json()["detail"] == "Query string too long"


def test_rejects_oversized_payload():
    # Force large content length with raw payload header
    huge = ("x" * (2 * 1024 * 1024)).encode("utf-8")
    response = client.post(
        "/api/webhooks/subscribe",
        content=huge,
        headers={"Content-Type": "application/json", "Content-Length": str(len(huge))},
    )
    assert response.status_code == 413
    assert response.json()["detail"] == "Request payload too large"
