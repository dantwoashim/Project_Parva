"""Integration tests for resolve/spec/provenance trace verification endpoints."""

from app.main import app
from fastapi.testclient import TestClient

from tests.helpers import TRUST_HEADERS

client = TestClient(app)


def test_resolve_endpoint_returns_expected_sections():
    resp = client.get("/v3/api/resolve", params={"date": "2026-10-15"})
    assert resp.status_code == 200
    body = resp.json()

    assert body["date"] == "2026-10-15"
    assert "bikram_sambat" in body
    assert "tithi" in body
    assert "panchanga" in body
    assert "observances" in body
    assert "trace" in body
    assert body["trace"]["trace_id"].startswith("tr_")


def test_resolve_uses_one_location_for_tithi_and_nested_panchanga():
    resp = client.get(
        "/v3/api/resolve",
        params={"date": "2026-10-15", "latitude": 40.7128, "longitude": -74.0060},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["tithi"]["sunrise_utc"] == body["panchanga"]["sunrise"]["utc"]


def test_resolve_endpoint_rejects_compact_date_format():
    resp = client.get("/v3/api/resolve", params={"date": "20261015"})

    assert resp.status_code == 400
    assert resp.json()["detail"] == "Invalid date format, use YYYY-MM-DD"


def test_spec_conformance_endpoint_returns_report():
    resp = client.get("/v3/api/spec/conformance", headers=TRUST_HEADERS)
    assert resp.status_code == 200
    body = resp.json()

    assert body["spec"]["version"] == "1.0"
    assert "conformance" in body
    assert "case_pack" in body


def test_spec_conformance_endpoint_is_public():
    resp = client.get("/v3/api/spec/conformance")
    assert resp.status_code == 200
    assert resp.json()["spec"]["version"] == "1.0"


def test_trace_verify_endpoint_validates_generated_trace():
    resolve_resp = client.get(
        "/v3/api/resolve", params={"date": "2026-10-16", "include_trace": True}
    )
    assert resolve_resp.status_code == 200
    trace_id = resolve_resp.json()["trace"]["trace_id"]

    verify_resp = client.get(f"/v3/api/provenance/verify/trace/{trace_id}", headers=TRUST_HEADERS)
    assert verify_resp.status_code == 200
    data = verify_resp.json()
    assert data["trace_id"] == trace_id
    assert data["checks"]["deterministic_id_match"] is True
