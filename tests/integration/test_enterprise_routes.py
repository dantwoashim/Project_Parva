"""Focused integration tests for enterprise calendar routes."""

from __future__ import annotations

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_capabilities_returns_evaluation_ready():
    response = client.get("/v3/api/enterprise/capabilities")
    assert response.status_code == 200
    body = response.json()
    assert body["surface"] == "enterprise_calendar"
    assert body["status"] == "evaluation_ready"
    assert "validation_suite" in body["stable"]
    assert body["source_provenance"]["official_structured_range"] == "2078-2083 BS"
    assert body["source_provenance"]["official_2070_2095_bundle_available"] is False


def test_fiscal_year_2082_returns_start_and_end():
    response = client.get("/v3/api/enterprise/fiscal-year/2082")
    assert response.status_code == 200
    body = response.json()
    assert body["fiscal_year"] == "2082/83"
    assert body["start"]["bs"] == "2082-04-01"
    assert body["start"]["ad"] == "2025-07-16"
    assert body["end"]["bs"] == "2083-03-32"
    assert body["end"]["ad"] == "2026-07-16"
    assert body["confidence"] == "derived_from_official_lookup"
    assert body["source_status"] == "structured_official"


def test_bs_months_returns_12_months():
    response = client.get("/v3/api/enterprise/bs-months/2082")
    assert response.status_code == 200
    body = response.json()
    assert body["bs_year"] == 2082
    assert len(body["months"]) == 12
    assert all(29 <= row["days"] <= 32 for row in body["months"])
    assert body["total_days"] == sum(row["days"] for row in body["months"])
    assert body["confidence"] == "official_lookup"
    assert body["source_status"] == "structured_official"


def test_bs_months_2085_is_not_marked_official():
    response = client.get("/v3/api/enterprise/bs-months/2085")
    assert response.status_code == 200
    body = response.json()
    assert body["bs_year"] == 2085
    assert body["confidence"] == "static_lookup_unverified"
    assert body["source_status"] == "static_table_unverified"
    assert body["official_structured_range"] == "2078-2083 BS"


def test_business_days_returns_count():
    response = client.post(
        "/v3/api/enterprise/business-days",
        json={
            "start_bs": "2082-04-01",
            "end_bs": "2082-04-31",
            "weekend": "saturday",
            "include_start": True,
            "include_end": True,
            "holiday_policy": "none",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["start_ad"] == "2025-07-16"
    assert body["end_ad"] == "2025-08-15"
    assert body["calendar_days"] == 31
    assert body["business_days"] == 27
    assert body["weekend_days"] == 4
    assert body["holiday_days"] == 0


def test_bulk_convert_ad_to_bs():
    response = client.post(
        "/v3/api/enterprise/bulk-convert",
        json={"mode": "ad_to_bs", "dates": ["2026-04-14"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] == 1
    assert body["failed"] == 0
    assert body["results"][0]["output"] == "2083-01-01"
    assert body["results"][0]["confidence"] == "official_lookup"


def test_bulk_convert_bs_to_ad():
    response = client.post(
        "/v3/api/enterprise/bulk-convert",
        json={"mode": "bs_to_ad", "dates": ["2083-01-01"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] == 1
    assert body["failed"] == 0
    assert body["results"][0]["output"] == "2026-04-14"
    assert body["results"][0]["confidence"] == "official_lookup"


def test_validate_passes_known_cases():
    response = client.post(
        "/v3/api/enterprise/validate",
        json={
            "cases": [
                {
                    "id": "ny-2083",
                    "type": "ad_to_bs",
                    "input": "2026-04-14",
                    "expected": "2083-01-01",
                }
            ]
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["passed"] == 1
    assert body["failed"] == 0
    assert body["pass_rate"] == 100.0
    assert body["results"][0]["passed"] is True


def test_validate_detects_mismatch():
    response = client.post(
        "/v3/api/enterprise/validate",
        json={
            "cases": [
                {
                    "id": "bad-ny",
                    "type": "ad_to_bs",
                    "input": "2026-04-14",
                    "expected": "2083-01-02",
                }
            ]
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["passed"] == 0
    assert body["failed"] == 1
    assert body["results"][0]["actual"] == "2083-01-01"
    assert body["results"][0]["passed"] is False


def test_invalid_bs_date_returns_error_result_in_bulk_conversion():
    response = client.post(
        "/v3/api/enterprise/bulk-convert",
        json={"mode": "bs_to_ad", "dates": ["2082-13-01"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] == 0
    assert body["failed"] == 1
    assert body["results"][0]["success"] is False
    assert body["results"][0]["error"]
