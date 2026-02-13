"""v4 contract tests for canonical data/meta envelope."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _assert_v4_envelope(body: dict):
    assert "data" in body
    assert "meta" in body
    meta = body["meta"]
    assert isinstance(meta, dict)
    assert "confidence" in meta
    assert "method" in meta
    assert "provenance" in meta
    assert "uncertainty" in meta
    assert "trace_id" in meta


def test_v4_docs_and_openapi_endpoints_exist():
    openapi_resp = client.get("/v4/openapi.json")
    assert openapi_resp.status_code == 200
    body = openapi_resp.json()
    assert "paths" in body

    docs_resp = client.get("/v4/docs", follow_redirects=False)
    assert docs_resp.status_code in {302, 307}


def test_v4_envelope_wraps_core_json_endpoints():
    endpoints = [
        "/v4/api/calendar/convert?date=2026-02-15",
        "/v4/api/calendar/panchanga?date=2026-02-15",
        "/v4/api/festivals/dashain/explain?year=2026",
        "/v4/api/reliability/status",
        "/v4/api/forecast/festivals?year=2030&festivals=dashain,tihar",
    ]
    for endpoint in endpoints:
        resp = client.get(endpoint)
        assert resp.status_code == 200, endpoint
        assert resp.headers.get("X-Parva-Engine") == "v4"
        _assert_v4_envelope(resp.json())


def test_v4_does_not_wrap_non_json_payloads():
    response = client.get("/v4/api/feeds/ical?years=1")
    assert response.status_code == 200
    assert "text/calendar" in response.headers.get("content-type", "").lower()


def test_v3_shape_is_kept_for_lts_compat():
    response = client.get("/v3/api/calendar/convert?date=2026-02-15")
    assert response.status_code == 200
    body = response.json()
    assert "data" not in body
    assert "meta" not in body
