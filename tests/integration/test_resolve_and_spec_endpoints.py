"""Integration tests for resolve/spec/provenance trace verification endpoints."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_resolve_endpoint_returns_expected_sections():
    resp = client.get("/v5/api/resolve", params={"date": "2026-10-15"})
    assert resp.status_code == 200
    body = resp.json()["data"]

    assert body["date"] == "2026-10-15"
    assert "bikram_sambat" in body
    assert "tithi" in body
    assert "panchanga" in body
    assert "observances" in body
    assert "trace" in body
    assert body["trace"]["trace_id"].startswith("tr_")


def test_spec_conformance_endpoint_returns_report():
    resp = client.get("/v5/api/spec/conformance")
    assert resp.status_code == 200
    body = resp.json()["data"]

    assert body["spec"]["version"] == "1.0"
    assert "conformance" in body
    assert "case_pack" in body


def test_trace_verify_endpoint_validates_generated_trace():
    resolve_resp = client.get("/v5/api/resolve", params={"date": "2026-10-16", "include_trace": True})
    assert resolve_resp.status_code == 200
    trace_id = resolve_resp.json()["data"]["trace"]["trace_id"]

    verify_resp = client.get(f"/v5/api/provenance/verify/trace/{trace_id}")
    assert verify_resp.status_code == 200
    data = verify_resp.json()["data"]
    assert data["trace_id"] == trace_id
    assert data["checks"]["deterministic_id_match"] is True
