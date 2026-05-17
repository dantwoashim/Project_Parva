from __future__ import annotations

import pytest
from app.sources.review_queue import build_source_review_queue

pytestmark = pytest.mark.research_artifact


def test_build_source_review_queue_has_priority_and_actions():
    payload = build_source_review_queue()

    assert payload["source_family"] == "moha_official"
    assert payload["inventory_path"] == "data/source_inventory/moha_official_years.json"
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


def test_source_review_queue_reads_committed_inventory():
    payload = build_source_review_queue()

    years = {item["bs_year"] for item in payload["items"]}
    assert {2076, 2082}.issubset(years)


def test_missing_inventory_has_explicit_empty_queue(monkeypatch, tmp_path):
    from app.sources import review_queue

    monkeypatch.setattr(review_queue, "MOHA_INVENTORY_PATH", tmp_path / "missing.json")
    payload = review_queue.build_source_review_queue()

    assert payload["total_items"] == 0
    assert payload["summary"]["critical"] == 0
