"""v5 authority-track contract tests."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _assert_v5_meta(meta: dict):
    assert "trace_id" in meta
    assert "method" in meta
    assert "confidence" in meta
    assert isinstance(meta["confidence"], dict)
    assert "level" in meta["confidence"]
    assert "score" in meta["confidence"]
    assert "provenance" in meta
    assert isinstance(meta["provenance"], dict)
    assert "dataset_hash" in meta["provenance"]
    assert "rules_hash" in meta["provenance"]
    assert "snapshot_id" in meta["provenance"]
    assert "verify_url" in meta["provenance"]
    assert "signature" in meta["provenance"]
    assert "uncertainty" in meta
    assert "boundary_risk" in meta["uncertainty"]
    assert "policy" in meta


def test_v5_docs_and_openapi_endpoints_exist():
    openapi_resp = client.get("/v5/openapi.json")
    assert openapi_resp.status_code == 200
    assert "paths" in openapi_resp.json()

    docs_resp = client.get("/v5/docs", follow_redirects=False)
    assert docs_resp.status_code in {302, 307}


def test_v5_envelope_wraps_core_endpoints():
    endpoints = [
        "/v5/api/calendar/convert?date=2026-02-15",
        "/v5/api/resolve?date=2026-10-15",
        "/v5/api/spec/conformance",
        "/v5/api/festivals/coverage",
    ]
    for endpoint in endpoints:
        resp = client.get(endpoint)
        assert resp.status_code == 200, endpoint
        assert resp.headers.get("X-Parva-Engine") == "v5"
        body = resp.json()
        assert "data" in body
        assert "meta" in body
        _assert_v5_meta(body["meta"])


def test_v5_non_json_feed_is_not_wrapped():
    response = client.get("/v5/api/integrations/feeds/all.ics?years=1")
    assert response.status_code == 200
    assert "text/calendar" in response.headers.get("content-type", "").lower()
