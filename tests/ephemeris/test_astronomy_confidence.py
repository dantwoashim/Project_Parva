from __future__ import annotations

from app.research.future_bs.astronomy_confidence import classify_astronomy_confidence


def test_confidence_separates_astronomy_from_civil_authority() -> None:
    payload = classify_astronomy_confidence(
        jpl_available=True,
        has_official_source=False,
        minutes_to_boundary=10,
    ).payload()

    assert payload["astronomy_status"] == "jpl_verified"
    assert payload["civil_authority_status"] == "computed_not_official"
    assert payload["review_required"] is True
    assert payload["boundary_risk"] == "high"


def test_boundary_risk_thresholds() -> None:
    assert classify_astronomy_confidence(jpl_available=False, minutes_to_boundary=240).boundary_risk == "low"
    assert classify_astronomy_confidence(jpl_available=False, minutes_to_boundary=120).boundary_risk == "medium"
    assert classify_astronomy_confidence(jpl_available=False, minutes_to_boundary=20).boundary_risk == "high"


def test_published_source_still_requires_review_without_official_source() -> None:
    payload = classify_astronomy_confidence(
        jpl_available=False,
        has_published_source=True,
        minutes_to_boundary=240,
    ).payload()

    assert payload["astronomy_status"] == "fallback_computed"
    assert payload["civil_authority_status"] == "published_source"
    assert payload["review_required"] is True
