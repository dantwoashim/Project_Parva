"""Source precedence tests (Week 8)."""

from app.calendar.calculator_v2 import calculate_festival_v2
from app.calendar.overrides import get_festival_override, get_festival_override_info
from app.sources.loader import DEFAULT_PRIORITY, get_source_loader


def test_source_priority_order_matches_policy_doc():
    loader = get_source_loader()
    assert loader.get_source_priority() == DEFAULT_PRIORITY
    assert loader.get_source_priority()[0] == "ground_truth_overrides"
    assert "secondary_digital_provider" in loader.get_source_priority()
    assert loader.get_source_priority().index("secondary_digital_provider") < loader.get_source_priority().index(
        "computed_ephemeris"
    )


def test_override_source_has_precedence_data():
    # dashain has official override entries in existing dataset
    info = get_festival_override_info("dashain", 2026)
    assert info is not None
    # Source metadata may be None in legacy rows; when present, it should be non-empty.
    if info.get("source") is not None:
        assert isinstance(info["source"], str)
        assert info["source"]


def test_ground_truth_loader_merges_supplemental_baseline_files():
    loader = get_source_loader()
    payload = loader.load_ground_truth()

    assert payload
    bs_years = payload.get("_meta", {}).get("bs_years", [])
    assert 2078 in bs_years
    assert 2079 in bs_years
    assert 2083 in bs_years
    assert any(
        row.get("festival_id") == "dashain" and row.get("gregorian_date") == "2026-10-11"
        for row in payload.get("records", [])
    )
    assert any(
        row.get("festival_id") == "dashain" and row.get("gregorian_date") == "2021-10-07"
        for row in payload.get("records", [])
    )
    validation = payload.get("_meta", {}).get("validation", {})
    assert validation.get("status") in {"ok", "warning"}
    assert validation.get("authority_mismatch_count", 0) >= 1


def test_secondary_digital_provider_enriches_historical_override_years():
    info = get_festival_override_info("bs-new-year", 1943)
    assert info is not None
    assert info["start"].isoformat() == "1943-04-14"
    assert info["source"] == "ratopati_calendar_digital_provider"
    assert info["confidence"] == "secondary"


def test_source_hint_can_select_alternate_authority_candidate():
    default_info = get_festival_override_info("dashain", 2026)
    hinted_info = get_festival_override_info("dashain", 2026, source_hint="nepal_gov")

    assert default_info is not None
    assert hinted_info is not None
    assert default_info["start"].isoformat() == "2026-10-11"
    assert hinted_info["start"].isoformat() == "2026-10-10"
    assert hinted_info["source"] == "nepal_gov"


def test_notes_hint_disambiguates_same_source_conflict():
    default_date = get_festival_override("shivaratri", 2026)
    hinted_date = get_festival_override(
        "shivaratri",
        2026,
        source_hint="moha_pdf_2082",
        notes_hint="Falgun 3 (MoHA 2082)",
    )

    assert default_date is not None
    assert hinted_date is not None
    assert default_date.isoformat() == "2026-02-15"
    assert hinted_date.isoformat() == "2026-02-14"


def test_calculator_source_aware_mode_resolves_estimated_track_without_official_override():
    default_result = calculate_festival_v2("shivaratri", 2027)
    estimated_result = calculate_festival_v2(
        "shivaratri",
        2027,
        source_hint="estimated",
        notes_hint="Falgun Krishna 14 2027",
    )

    assert default_result is not None
    assert estimated_result is not None
    assert default_result.start_date.isoformat() == "2027-03-06"
    assert estimated_result.start_date.isoformat() == "2027-03-05"
