"""Week 25-28 tests for OCR ingest normalization helpers."""

from __future__ import annotations

from backend.tools.ingest_moha_pdfs import (
    HolidayEntry,
    deduplicate_entries,
    normalize_ocr_text,
)


def test_normalize_ocr_text_applies_common_substitutions():
    raw = "संक्रान्ति वेशाख १२ गते"
    normalized = normalize_ocr_text(raw)
    assert "सङ्क्रान्ति" in normalized
    assert "वैशाख" in normalized


def test_deduplicate_entries_prefers_higher_confidence():
    rows = [
        HolidayEntry(
            bs_year=2082,
            name_raw="घटस्थापना",
            month_raw="असोज",
            day_raw="१",
            month_num=6,
            day_num=1,
            line="घटस्थापना - असोज १ गते",
            matched_id="dashain",
            parse_confidence="medium",
        ),
        HolidayEntry(
            bs_year=2082,
            name_raw="घटस्थापना",
            month_raw="असोज",
            day_raw="१",
            month_num=6,
            day_num=1,
            line="घटस्थापना - असोज १ गते",
            matched_id="dashain",
            parse_confidence="high",
        ),
    ]

    deduped = deduplicate_entries(rows)
    assert len(deduped) == 1
    assert deduped[0].parse_confidence == "high"
