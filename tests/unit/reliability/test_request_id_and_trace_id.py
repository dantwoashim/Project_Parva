from __future__ import annotations

from app.bootstrap.app_factory import create_app
from fastapi.testclient import TestClient


def test_request_id_is_propagated_as_trace_id(monkeypatch):
    monkeypatch.setenv("PARVA_RATE_LIMIT_ENABLED", "false")
    client = TestClient(create_app())

    response = client.get("/health/live", headers={"X-Request-ID": "phase08-trace"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "phase08-trace"
    assert response.headers["X-Trace-ID"] == "phase08-trace"
