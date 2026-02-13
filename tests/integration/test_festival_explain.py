"""Week 38 integration tests for festival explain endpoint."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_festival_explain_endpoint_returns_human_readable_payload():
    resp = client.get("/api/festivals/dashain/explain", params={"year": 2026})
    assert resp.status_code == 200

    body = resp.json()
    assert body["festival_id"] == "dashain"
    assert body["year"] == 2026
    assert isinstance(body["steps"], list)
    assert len(body["steps"]) >= 3
    assert "calculation_trace_id" in body


def test_festival_explain_endpoint_available_on_v2_alias():
    resp = client.get("/v2/api/festivals/dashain/explain", params={"year": 2026})
    assert resp.status_code == 200
    assert resp.json()["festival_id"] == "dashain"


def test_trace_endpoint_returns_structured_reason_trace():
    resp = client.get("/api/festivals/dashain/explain", params={"year": 2026})
    assert resp.status_code == 200
    trace_id = resp.json()["calculation_trace_id"]

    trace_resp = client.get(f"/api/explain/{trace_id}")
    assert trace_resp.status_code == 200
    trace = trace_resp.json()
    assert trace["trace_id"] == trace_id
    assert trace["trace_type"] == "festival_date_explain"
    assert isinstance(trace["steps"], list)
    assert len(trace["steps"]) >= 1
    assert trace["policy"]["usage"] == "informational"


def test_trace_id_is_stable_for_same_festival_year():
    r1 = client.get("/api/festivals/dashain/explain", params={"year": 2026})
    r2 = client.get("/api/festivals/dashain/explain", params={"year": 2026})
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["calculation_trace_id"] == r2.json()["calculation_trace_id"]
