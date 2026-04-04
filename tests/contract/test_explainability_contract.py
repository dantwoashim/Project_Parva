"""Contract checks for explainability API surfaces."""

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_explain_trace_list_endpoint_exists():
    resp = client.get("/api/explain", params={"limit": 5})
    assert resp.status_code == 200
    body = resp.json()
    assert "traces" in body
    assert body["policy"]["usage"] == "informational"


def test_explain_trace_available_v2_alias():
    explain = client.get("/api/festivals/dashain/explain", params={"year": 2026})
    assert explain.status_code == 200
    trace_id = explain.json()["calculation_trace_id"]

    trace_resp = client.get(f"/v3/api/explain/{trace_id}")
    assert trace_resp.status_code == 200
    trace_body = trace_resp.json()
    assert trace_body["trace_id"] == trace_id
    assert isinstance(trace_body["steps"], list)


def test_private_personal_trace_is_not_publicly_retrievable():
    resp = client.get(
        "/api/personal/panchanga",
        params={"date": "2026-02-15", "lat": "27.7172", "lon": "85.324", "tz": "Asia/Kathmandu"},
    )
    assert resp.status_code == 200
    trace_id = resp.json()["calculation_trace_id"]

    trace_resp = client.get(f"/api/explain/{trace_id}")
    assert trace_resp.status_code == 404


def test_public_provenance_root_is_available_on_v3_surface():
    resp = client.get("/v3/api/provenance/root")
    assert resp.status_code == 200
    assert "merkle_root" in resp.json()
