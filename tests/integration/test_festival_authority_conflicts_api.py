"""Festival API checks for authority conflict surfacing."""

from __future__ import annotations

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_festival_detail_exposes_authority_conflict_metadata():
    response = client.get("/api/festivals/ghode-jatra", params={"year": 2026})
    assert response.status_code == 200

    body = response.json()
    assert body["dates"]["authority_conflict"] is True
    assert body["dates"]["authority_candidate_count"] >= 2
    assert "Multiple authority candidates exist" in body["dates"]["authority_note"]
    assert any(
        row["start"] == "2026-03-17" for row in body["dates"]["authority_alternates"]
    )
    assert any(
        row["start"] == "2026-03-17" for row in body["dates"]["alternate_candidates"]
    )
    assert body["dates"]["authority_suggested_profile_id"] == "published-holiday-listing"
    assert body["dates"]["authority_suggested_start_date"] == "2026-03-17"
    assert body["dates"]["selection_policy"] == "public_default"
    assert body["dates"]["source_family"]
    assert body["dates"]["engine_path"]
    assert body["dates"]["calibration_status"] in {"not_applicable", "unavailable"}


def test_festival_explain_mentions_authority_conflict_when_present():
    response = client.get("/api/festivals/ghode-jatra/explain", params={"year": 2026})
    assert response.status_code == 200

    body = response.json()
    assert any("candidate date entries" in step for step in body["steps"])
    assert "Multiple authority candidates exist" in body["explanation"]
    assert body["authority_conflict"] is True
    assert body["selection_policy"] == "public_default"
    assert body["source_family"]
    assert len(body["alternate_candidates"]) >= 1
    assert body["authority_suggested_profile_id"] == "published-holiday-listing"
    assert body["authority_suggested_start_date"] == "2026-03-17"


def test_festival_detail_supports_authority_compare_mode():
    response = client.get(
        "/api/festivals/ghode-jatra",
        params={"year": 2026, "authority_mode": "authority_compare"},
    )
    assert response.status_code == 200

    body = response.json()
    assert body["dates"]["selection_policy"] == "authority_compare"
    assert body["dates"]["authority_conflict"] is True
    assert "compare mode" in body["dates"]["authority_note"].lower()


def test_festival_explain_supports_all_candidates_mode():
    response = client.get(
        "/api/festivals/ghode-jatra/explain",
        params={"year": 2026, "authority_mode": "all_candidates"},
    )
    assert response.status_code == 200

    body = response.json()
    assert body["selection_policy"] == "all_candidates"
    assert body["authority_conflict"] is True
    assert len(body["alternate_candidates"]) >= 1
    assert any("all published candidates are surfaced" in step.lower() for step in body["steps"])


def test_festivals_on_date_surfaces_conflict_note():
    response = client.get("/api/festivals/on-date/2026-03-18")
    assert response.status_code == 200

    body = response.json()
    ghode_jatra = next(row for row in body if row["id"] == "ghode-jatra")
    assert "Multiple authority candidates exist" in ghode_jatra["date_status_note"]


def test_festival_detail_applies_profile_variant_when_available():
    response = client.get(
        "/api/festivals/shivaratri",
        params={"year": 2026, "profile": "diaspora-north-indian"},
    )
    assert response.status_code == 200

    body = response.json()
    assert body["dates"]["start_date"] == "2026-02-15"
    assert body["dates"]["profile_id"] == "diaspora-north-indian"
    assert body["dates"]["profile_note"]


def test_festival_explain_applies_profile_variant_when_available():
    response = client.get(
        "/api/festivals/shivaratri/explain",
        params={"year": 2026, "profile": "diaspora-north-indian"},
    )
    assert response.status_code == 200

    body = response.json()
    assert body["start_date"] == "2026-02-15"
    assert body["profile_id"] == "diaspora-north-indian"
    assert any("Apply profile variant" in step for step in body["steps"])


def test_festival_detail_applies_year_scoped_published_listing_variant():
    response = client.get(
        "/api/festivals/ram-navami",
        params={"year": 2026, "profile": "published-holiday-listing"},
    )
    assert response.status_code == 200

    body = response.json()
    assert body["dates"]["start_date"] == "2026-03-26"
    assert body["dates"]["profile_id"] == "published-holiday-listing"
    assert "alternate" in body["dates"]["profile_note"].lower()


def test_profile_variant_stays_scoped_to_documented_years():
    response = client.get(
        "/api/festivals/shivaratri",
        params={"year": 2027, "profile": "diaspora-north-indian"},
    )
    assert response.status_code == 200

    body = response.json()
    assert body["dates"]["start_date"] == "2027-03-06"
    assert body["dates"]["profile_id"] == "diaspora-north-indian"
    assert "No dedicated diaspora-north-indian variant" in body["dates"]["profile_note"]


def test_variants_endpoint_auto_generates_authority_profile_variant():
    response = client.get(
        "/api/festivals/ram-navami/variants",
        params={"year": 2026, "profile": "published-holiday-listing"},
    )
    assert response.status_code == 200

    body = response.json()
    assert any(variant["date"] == "2026-03-26" for variant in body["variants"])
    assert any(variant["auto_generated"] is True for variant in body["variants"])


def test_upcoming_endpoint_respects_profile_shifted_dates():
    response = client.get(
        "/api/festivals/upcoming",
        params={"from_date": "2026-03-17", "days": 1, "profile": "published-holiday-listing"},
    )
    assert response.status_code == 200

    body = response.json()
    ghode_jatra = next(row for row in body["festivals"] if row["id"] == "ghode-jatra")
    assert ghode_jatra["start_date"] == "2026-03-17"
    assert ghode_jatra["profile_id"] == "published-holiday-listing"


def test_on_date_endpoint_respects_profile_shifted_dates():
    default_response = client.get("/api/festivals/on-date/2026-03-18")
    assert default_response.status_code == 200
    default_ids = {row["id"] for row in default_response.json()}
    assert "ghode-jatra" in default_ids

    profile_response = client.get(
        "/api/festivals/on-date/2026-03-17",
        params={"profile": "published-holiday-listing"},
    )
    assert profile_response.status_code == 200
    profile_ids = {row["id"] for row in profile_response.json()}
    assert "ghode-jatra" in profile_ids


def test_calendar_endpoint_respects_profile_shifted_dates():
    response = client.get(
        "/api/festivals/calendar/2026/3",
        params={"profile": "published-holiday-listing"},
    )
    assert response.status_code == 200

    body = response.json()
    march_17 = next(day for day in body["days"] if day["date"] == "2026-03-17")
    assert any(festival["id"] == "ghode-jatra" for festival in march_17["festivals"])
