"""Route-level proof contract matrix for stable public proof routes."""

from __future__ import annotations

from app.main import app
from app.membranes.verifier import verify_membrane
from fastapi.testclient import TestClient

client = TestClient(app)

PROOF_MODES = ("none", "compact", "audit", "replay", "membrane")


def _request(case: dict, proof: str):
    params = dict(case.get("params", {}))
    params["proof"] = proof
    if case["method"] == "GET":
        return client.get(case["path"], params=params)
    return client.post(case["path"], params=params, json=case.get("json", {}))


ROUTE_CASES = [
    {
        "name": "bs_to_ad",
        "method": "POST",
        "path": "/v3/api/calendar/bs-to-gregorian",
        "json": {"year": 2082, "month": 1, "day": 1},
        "operation": "convert_bs_to_ad",
    },
    {
        "name": "ad_to_bs",
        "method": "GET",
        "path": "/v3/api/calendar/convert",
        "params": {"date": "2025-04-14"},
        "operation": "ad_to_bs",
    },
    {
        "name": "validate_bs_date",
        "method": "GET",
        "path": "/v3/api/calendar/validate-bs-date",
        "params": {"year": 2082, "month": 1, "day": 1},
        "operation": "validate_bs_date",
    },
    {
        "name": "holiday",
        "method": "GET",
        "path": "/v3/api/compliance/holiday",
        "params": {"bs_date": "2082-01-01"},
        "operation": "holiday",
    },
    {
        "name": "working_day",
        "method": "POST",
        "path": "/v3/api/compliance/evaluate-date",
        "json": {"profile_id": "nepal_private_company_default", "bs_date": "2082-01-02", "decision_intent": "general"},
        "operation": "working_day",
    },
    {
        "name": "fiscal_year",
        "method": "GET",
        "path": "/v3/api/enterprise/fiscal-year/2082",
        "operation": "fiscal_year",
    },
    {
        "name": "bs_months",
        "method": "GET",
        "path": "/v3/api/enterprise/bs-months/2082",
        "params": {"mode": "canonical"},
        "operation": "bs_months",
    },
    {
        "name": "panchanga_summary",
        "method": "GET",
        "path": "/v3/api/calendar/panchanga",
        "params": {
            "date": "2025-04-14",
            "ephemeris_provider": "pinned_panchanga_fixture",
            "ephemeris_fixture_id": "kathmandu_2025_04_14_lahiri",
            "lat": 27.7172,
            "lon": 85.324,
            "tz": "Asia/Kathmandu",
        },
        "operation": "panchanga_summary",
    },
]


def test_route_proof_matrix_artifact_exists_and_covers_routes() -> None:
    import json
    from pathlib import Path

    matrix = json.loads(Path("reports/proof_contract/route_proof_matrix.json").read_text(encoding="utf-8"))
    operations = {route["operation"] for route in matrix["routes"]}
    assert {case["name"] for case in ROUTE_CASES}.issubset(operations | {"bs_to_ad"})
    assert matrix["required_proof_modes"] == list(PROOF_MODES)


def test_stable_routes_support_all_documented_proof_modes() -> None:
    for case in ROUTE_CASES:
        for proof_mode in PROOF_MODES:
            response = _request(case, proof_mode)
            assert response.status_code == 200, (case["name"], proof_mode, response.text)
            body = response.json()
            if proof_mode == "none":
                assert body.get("proof") is None
                assert body.get("meta") or body.get("policy") or body.get("not_authority") is not False
                continue

            proof = body["proof"]
            capsule = proof["capsule"]
            assert proof["mode"] == proof_mode
            assert proof["identity_hash"].startswith("parva:id:v1:sha256:")
            assert proof["witness_hash"].startswith("parva:wit:v1:sha256:")
            assert proof["field_provenance"]
            assert proof["boundary_vector"]["not_authority"] is True
            assert proof["proof_pack"]["steps"]
            assert verify_membrane(capsule) == (True, "verified")
            assert capsule["canonical_query"]["operation"] == case["operation"]
            assert "government_authority" not in str(proof).lower()
            assert "payroll_final_authority" in str(proof["boundary_vector"].get("blocked_use_cases", []))
            if case["name"] == "panchanga_summary":
                assert capsule["boundary"]["not_panchanga_authority"] is True
                assert capsule["boundary"]["not_ritual_final_authority"] is True
                assert capsule["ephemeris_metadata"]["jpl_backed"] is False


def test_invalid_and_unsupported_proof_inputs_remain_bounded() -> None:
    invalid = client.get(
        "/v3/api/calendar/validate-bs-date",
        params={"year": 2082, "month": 1, "day": 32, "proof": "replay"},
    )
    assert invalid.status_code == 200
    invalid_body = invalid.json()
    assert invalid_body["valid"] is False
    assert invalid_body["proof"]["capsule"]["membrane_kind"] == "negative"
    assert invalid_body["proof"]["boundary_vector"]["not_authority"] is True

    unsupported_mode = client.get("/v3/api/calendar/convert", params={"date": "2025-04-14", "proof": "banana"})
    assert unsupported_mode.status_code == 200
    assert unsupported_mode.json().get("proof") is None

    static_lookup = client.get(
        "/v3/api/enterprise/bs-months/2082",
        params={"mode": "static_lookup", "proof": "audit"},
    )
    assert static_lookup.status_code == 200
    boundary = static_lookup.json()["proof"]["boundary_vector"]
    assert boundary["authority"] != "structured_official"

    panchanga = client.get(
        "/v3/api/calendar/panchanga",
        params={
            "date": "2025-04-14",
            "proof": "audit",
            "ephemeris_provider": "pinned_panchanga_fixture",
            "ephemeris_fixture_id": "kathmandu_2025_04_14_lahiri",
        },
    )
    assert panchanga.status_code == 200
    assert panchanga.json()["proof"]["capsule"]["ephemeris_metadata"]["jpl_backed"] is False
