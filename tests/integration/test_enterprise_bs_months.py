"""Phase 00 trust-arrest regression tests for enterprise BS month metadata."""

from __future__ import annotations

from app.calendar.bikram_sambat import days_in_bs_month
from app.calendar.sankranti import compute_bs_month_lengths
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def _days(body: dict) -> list[int]:
    return [int(row["days"]) for row in body["months"]]


def test_2087_default_canonical_does_not_emit_static_table_truth() -> None:
    response = client.get("/v3/api/enterprise/bs-months/2087")

    assert response.status_code == 200
    body = response.json()
    assert body["calculation_mode"] == "canonical"
    assert body["requested_mode"] == "canonical"
    assert body["selected_method"] == "solar_civil"
    assert body["result"]["total_days"] == 365
    assert body["policy_decision"]["not_authority"] is True
    assert body["boundary"]["not_authority"] is True
    assert body["boundary"]["review_state"] == "required"
    assert "total_days" in body["field_provenance"]
    assert body["field_provenance"]["total_days"]["authority"] == "computed_uncertified"
    assert body["selected_mode"] == "solar_civil"
    assert body["total_days"] == 365
    assert _days(body) == compute_bs_month_lengths(2087)
    assert _days(body) != [days_in_bs_month(2087, month) for month in range(1, 13)]
    assert body["confidence"] == "canonical_solar_civil_computed"
    assert body["source_status"] == "computed_solar_civil"
    assert body["review_required"] is True
    assert body["not_authority"] is True
    assert body["meta"]["confidence"] == body["confidence"]
    assert body["meta"]["source"]["id"] == "parva_astronomical_engine"
    assert "source_backed" not in body["meta"]["confidence"]


def test_2087_static_lookup_is_explicit_unverified_and_review_required() -> None:
    response = client.get("/v3/api/enterprise/bs-months/2087", params={"mode": "static_lookup"})

    assert response.status_code == 200
    body = response.json()
    assert body["calculation_mode"] == "static_lookup"
    assert body["total_days"] == 367
    assert body["confidence"] == "static_lookup_unverified"
    assert body["source_status"] == "static_reference"
    assert body["authority"] == "static_reference"
    assert body["review_required"] is True
    assert body["not_authority"] is True
    assert body["meta"]["confidence"] == "static_lookup_unverified"
    assert body["meta"]["source"]["id"] == "parva_static_lookup_table"
    assert "government_calendar_publication" in body["blocked_use_cases"]


def test_2087_compare_returns_structured_branches() -> None:
    response = client.get("/v3/api/enterprise/bs-months/2087", params={"mode": "compare"})

    assert response.status_code == 200
    body = response.json()
    assert body["calculation_mode"] == "compare"
    assert body["requested_mode"] == "compare"
    assert body["membrane_kind"] == "branch_set"
    assert body["branch_set"]["membrane_kind"] == "branch_set"
    assert {branch["branch_id"] for branch in body["branch_set"]["branches"]} == {
        "canonical",
        "solar_civil",
        "static_lookup",
    }
    assert body["result"]["disagreement"] is True
    assert body["policy_decision"]["decision_trace"][0] == "compare_mode_requested"
    assert body["field_provenance"]["branches"]["flags"] == ["review_required", "source_conflict"]
    assert body["default_branch"] == "canonical"
    assert body["selected_mode"] == "canonical"
    assert set(body["branches"]) == {"canonical", "solar_civil", "static_lookup"}
    assert body["branches"]["canonical"]["total_days"] == 365
    assert body["branches"]["solar_civil"]["total_days"] == 365
    assert body["branches"]["static_lookup"]["total_days"] == 367
    assert body["branches"]["static_lookup"]["confidence"] == "static_lookup_unverified"
    assert body["branches"]["static_lookup"]["review_required"] is True
    assert body["disagreement"] is True
    assert body["review_required"] is True
    assert body["meta"]["confidence"] == "comparison_requires_review"


def test_2096_future_static_table_year_is_not_upgraded_to_source_backed() -> None:
    default_response = client.get("/v3/api/enterprise/bs-months/2096")
    static_response = client.get(
        "/v3/api/enterprise/bs-months/2096",
        params={"mode": "static_lookup"},
    )

    assert default_response.status_code == 200
    assert static_response.status_code == 200
    default_body = default_response.json()
    static_body = static_response.json()
    assert default_body["calculation_mode"] == "canonical"
    assert default_body["source_status"] == "computed_solar_civil"
    assert default_body["meta"]["source"]["id"] == "parva_astronomical_engine"
    assert static_body["calculation_mode"] == "static_lookup"
    assert static_body["confidence"] == "static_lookup_unverified"
    assert static_body["source_status"] == "static_reference"
    assert static_body["meta"]["confidence"] == "static_lookup_unverified"
    assert static_body["review_required"] is True


def test_bs_month_mode_validation_rejects_implicit_table_alias() -> None:
    response = client.get("/v3/api/enterprise/bs-months/2087", params={"mode": "table"})

    assert response.status_code == 422
