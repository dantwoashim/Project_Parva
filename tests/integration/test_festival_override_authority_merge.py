"""Authority merge checks for festival override enrichment."""

from __future__ import annotations

from app.calendar.overrides import get_festival_override, get_festival_override_info


def test_evaluation_rows_enrich_existing_override_metadata():
    info = get_festival_override_info("bs-new-year", 2026)

    assert info is not None
    assert info["start"].isoformat() == "2026-04-14"
    assert info["source"] in {"nepal_gov", "moha_pdf_2083"}
    assert info["confidence"] == "official"
    assert info["candidate_count"] >= 1


def test_conflicting_authority_rows_are_preserved_as_alternates():
    chosen = get_festival_override("ghode-jatra", 2026)
    info = get_festival_override_info("ghode-jatra", 2026)

    assert chosen is not None
    assert chosen.isoformat() == "2026-03-17"
    assert info is not None
    assert info["candidate_count"] >= 2
    assert any(alt["start"].isoformat() == "2026-03-18" for alt in info["alternates"])
    assert info["suggested_profile_id"] == "published-holiday-listing"
    assert info["suggested_start"].isoformat() == "2026-03-18"
