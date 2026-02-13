"""Contract checks for explainability API surfaces."""

from fastapi.testclient import TestClient

from app.main import app


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

    trace_resp = client.get(f"/v2/api/explain/{trace_id}")
    assert trace_resp.status_code == 200
    trace_body = trace_resp.json()
    assert trace_body["trace_id"] == trace_id
    assert isinstance(trace_body["steps"], list)
