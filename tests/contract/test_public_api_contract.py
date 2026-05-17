"""Public API reliability contract checks."""

from __future__ import annotations

from app.main import app
from app.membranes.verifier import verify_membrane
from fastapi.testclient import TestClient

client = TestClient(app)


def _assert_error_envelope(body: dict, *, code: str) -> None:
    assert "detail" in body
    assert body["error"]["code"] == code
    assert isinstance(body["error"]["message"], str)
    assert isinstance(body["error"]["details"], dict)
    assert body["error"]["trace_id"] == body["request_id"]
    assert body["version"] == "3.0.0"


def test_core_public_endpoints_have_stable_shapes() -> None:
    today = client.get("/v3/api/calendar/today")
    assert today.status_code == 200
    today_body = today.json()
    assert "gregorian" in today_body
    assert "bikram_sambat" in today_body

    convert = client.get("/v3/api/calendar/convert", params={"date": "2026-04-14"})
    assert convert.status_code == 200
    convert_body = convert.json()
    assert convert_body["policy"]["publication_status"] == "computed_prediction_not_official"
    assert convert_body["provenance"]["manifest_version"]
    assert convert_body["support_tier"]

    bs_to_ad = client.post(
        "/v3/api/calendar/bs-to-gregorian",
        json={"year": 2083, "month": 1, "day": 1},
    )
    assert bs_to_ad.status_code == 200
    bs_to_ad_body = bs_to_ad.json()
    assert bs_to_ad_body["policy"]["publication_status"] == "computed_prediction_not_official"
    assert bs_to_ad_body["provenance"]["manifest_version"]
    assert bs_to_ad_body["bs"]["confidence"]

    month = client.get("/v3/api/calendar/dual-month", params={"year": 2026, "month": 4})
    assert month.status_code == 200
    month_body = month.json()
    assert month_body["year"] == 2026
    assert month_body["month"] == 4
    assert month_body["days"]
    assert month_body["policy"]["publication_status"] == "computed_prediction_not_official"

    fiscal = client.get("/v3/api/enterprise/fiscal-year/2082")
    assert fiscal.status_code == 200
    fiscal_body = fiscal.json()
    assert fiscal_body["policy"]["publication_status"] == "computed_prediction_not_official"
    assert "fiscal_year" in fiscal_body

    months = client.get("/v3/api/enterprise/bs-months/2082")
    assert months.status_code == 200
    months_body = months.json()
    assert months_body["policy"]["publication_status"] == "computed_prediction_not_official"
    assert len(months_body["months"]) == 12

    business_days = client.post(
        "/v3/api/enterprise/business-days",
        json={"start_bs": "2082-01-01", "end_bs": "2082-01-07"},
    )
    assert business_days.status_code == 200
    assert "business_days" in business_days.json()

    capabilities = client.get("/v3/api/enterprise/capabilities")
    assert capabilities.status_code == 200
    assert capabilities.json()["publication_status"] == "computed_prediction_not_official"

    policy = client.get("/v3/api/policy")
    assert policy.status_code == 200
    assert "policy" in policy.json()


def test_public_errors_have_stable_envelope() -> None:
    bad_ad = client.get("/v3/api/calendar/convert", params={"date": "not-a-date"})
    assert bad_ad.status_code == 400
    _assert_error_envelope(bad_ad.json(), code="BAD_REQUEST")

    bad_bs = client.post(
        "/v3/api/calendar/bs-to-gregorian",
        json={"year": 2083, "month": 13, "day": 1},
    )
    assert bad_bs.status_code == 400
    _assert_error_envelope(bad_bs.json(), code="BAD_REQUEST")

    validation_error = client.get("/v3/api/calendar/dual-month", params={"year": 2026, "month": 13})
    assert validation_error.status_code == 422
    validation_body = validation_error.json()
    _assert_error_envelope(validation_body, code="REQUEST_VALIDATION_ERROR")
    assert "errors" in validation_body


def test_public_openapi_lists_core_surfaces() -> None:
    response = client.get("/v3/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]

    expected_paths = {
        "/v3/api/calendar/today",
        "/v3/api/calendar/convert",
        "/v3/api/calendar/bs-to-gregorian",
        "/v3/api/calendar/validate-bs-date",
        "/v3/api/calendar/dual-month",
        "/v3/api/compliance/holiday",
        "/v3/api/compliance/evaluate-date",
        "/v3/api/enterprise/capabilities",
        "/v3/api/enterprise/fiscal-year/{bs_year}",
        "/v3/api/enterprise/bs-months/{bs_year}",
        "/v3/api/enterprise/business-days",
        "/v3/api/policy",
    }

    assert expected_paths.issubset(paths)


def test_core_conversion_endpoint_emits_membrane_when_requested() -> None:
    response = client.post(
        "/v3/api/calendar/bs-to-gregorian",
        params={"proof": "membrane"},
        json={"year": 2082, "month": 1, "day": 1},
    )

    assert response.status_code == 200
    proof = response.json()["proof"]
    assert proof["mode"] == "membrane"
    assert proof["identity_hash"].startswith("parva:id:v1:sha256:")
    assert proof["witness_hash"].startswith("parva:wit:v1:sha256:")
    assert proof["capsule"]["source_resolution"]["eligible_official"] is False


def test_core_conversion_membrane_verifies() -> None:
    response = client.post(
        "/v3/api/calendar/bs-to-gregorian?proof=membrane",
        json={"year": 2082, "month": 1, "day": 1},
    )

    assert response.status_code == 200
    assert verify_membrane(response.json()["proof"]["capsule"]) == (True, "verified")


def test_core_conversion_field_provenance_complete() -> None:
    response = client.post(
        "/v3/api/calendar/bs-to-gregorian?proof=membrane",
        json={"year": 2082, "month": 1, "day": 1},
    )

    provenance = response.json()["proof"]["field_provenance"]
    assert set(provenance) == {"ad_date"}
    assert provenance["ad_date"]["authority"] == "static_reference"
    assert "review_required" in provenance["ad_date"]["flags"]


def test_core_conversion_no_sample_docket_outside_coverage() -> None:
    response = client.post(
        "/v3/api/calendar/bs-to-gregorian?proof=membrane",
        json={"year": 2099, "month": 1, "day": 1},
    )

    assert response.status_code == 200
    proof = response.json()["proof"]
    assert proof["source_docket_refs"] == []
    assert proof["boundary_vector"]["authority"] == "computed_uncertified"


def test_ad_to_bs_endpoint_emits_replayable_membrane_when_requested() -> None:
    response = client.get("/v3/api/calendar/convert", params={"date": "2025-04-14", "proof": "membrane"})

    assert response.status_code == 200
    proof = response.json()["proof"]
    assert proof["capsule"]["canonical_query"]["operation"] == "ad_to_bs"
    assert proof["capsule"]["result"]["bs_date"] == "2082-01-01"
    assert verify_membrane(proof["capsule"]) == (True, "verified")


def test_validate_bs_date_endpoint_emits_replayable_negative_membrane() -> None:
    response = client.get(
        "/v3/api/calendar/validate-bs-date",
        params={"year": 2082, "month": 1, "day": 32, "proof": "membrane"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is False
    proof = body["proof"]
    assert proof["capsule"]["canonical_query"]["operation"] == "validate_bs_date"
    assert proof["capsule"]["membrane_kind"] == "negative"
    assert verify_membrane(proof["capsule"]) == (True, "verified")


def test_holiday_endpoint_emits_replayable_membership_membrane() -> None:
    response = client.get(
        "/v3/api/compliance/holiday",
        params={"bs_date": "2082-01-01", "proof": "membrane"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["is_holiday"] is True
    proof = body["proof"]
    assert proof["capsule"]["canonical_query"]["operation"] == "holiday"
    assert proof["capsule"]["result"]["membership_proof"]["proof_type"] == "membership"
    assert verify_membrane(proof["capsule"]) == (True, "verified")


def test_working_day_endpoint_emits_replayable_policy_membrane() -> None:
    response = client.post(
        "/v3/api/compliance/evaluate-date?proof=membrane",
        json={"profile_id": "nepal_private_company_default", "bs_date": "2082-01-01", "decision_intent": "general"},
    )

    assert response.status_code == 200
    proof = response.json()["proof"]
    assert proof["capsule"]["canonical_query"]["operation"] == "working_day"
    assert "decision_support" in proof["boundary_vector"]["claim_boundary"]
    assert verify_membrane(proof["capsule"]) == (True, "verified")


def test_fiscal_year_endpoint_emits_replayable_membrane_when_requested() -> None:
    response = client.get("/v3/api/enterprise/fiscal-year/2082", params={"proof": "membrane"})

    assert response.status_code == 200
    proof = response.json()["proof"]
    assert proof["capsule"]["canonical_query"]["operation"] == "fiscal_year"
    assert "legal_tax" in proof["boundary_vector"]["claim_boundary"]
    assert verify_membrane(proof["capsule"]) == (True, "verified")


def test_bs_months_endpoint_emits_replayable_membrane_when_requested() -> None:
    response = client.get("/v3/api/enterprise/bs-months/2082", params={"mode": "canonical", "proof": "membrane"})

    assert response.status_code == 200
    proof = response.json()["proof"]
    assert proof["capsule"]["canonical_query"]["operation"] == "bs_months"
    assert proof["capsule"]["result"]["requested_mode"] == "canonical"
    assert verify_membrane(proof["capsule"]) == (True, "verified")
