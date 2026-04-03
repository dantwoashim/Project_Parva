from __future__ import annotations

from app.sources.review_queue import build_source_review_queue


def test_build_source_review_queue_has_priority_and_actions():
    payload = build_source_review_queue()

    assert payload["source_family"] == "moha_official"
    assert payload["total_items"] >= 1
    assert isinstance(payload["items"], list)
    first = payload["items"][0]
    assert first["review_priority"] in {"critical", "high", "medium", "low"}
    assert first["review_action"] in {
        "reacquire_source",
        "improve_extraction",
        "audit_structured_artifacts",
        "review_and_promote",
        "inventory_review",
    }
    assert isinstance(first["reasons"], list)


def test_archived_raw_pdf_years_are_queued_for_extraction_improvement():
    payload = build_source_review_queue()
    year_2076 = next(item for item in payload["items"] if item["bs_year"] == 2076)

    assert year_2076["status"] == "archived_raw_pdf"
    assert year_2076["review_action"] == "improve_extraction"
    assert year_2076["review_priority"] == "high"
    assert "structured_artifacts_missing" in year_2076["reasons"]
