"""Public API reliability contract checks."""

from __future__ import annotations

from app.main import app
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
        "/v3/api/calendar/dual-month",
        "/v3/api/enterprise/capabilities",
        "/v3/api/enterprise/fiscal-year/{bs_year}",
        "/v3/api/enterprise/bs-months/{bs_year}",
        "/v3/api/enterprise/business-days",
        "/v3/api/policy",
    }

    assert expected_paths.issubset(paths)
