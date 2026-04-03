from __future__ import annotations

from app.sources.validation import validate_ground_truth_payload


def test_validate_ground_truth_payload_flags_undeclared_authority_mismatches_as_errors():
    payload = {
        "records": [
            {
                "festival_id": "shivaratri",
                "bs_year": 2082,
                "bs_month": 11,
                "bs_day": 3,
                "gregorian_date": "2026-02-15",
                "override_date": {"start": "2026-02-14"},
            }
        ]
    }

    summary = validate_ground_truth_payload(payload)

    assert summary["status"] == "error"
    assert summary["authority_mismatch_count"] == 1
    assert summary["declared_conflict_count"] == 0
    assert summary["duplicate_record_count"] == 0


def test_validate_ground_truth_payload_treats_declared_conflicts_as_visible_but_non_fatal():
    payload = {
        "_meta": {"bs_years": [2082]},
        "records": [
            {
                "festival_id": "shivaratri",
                "bs_year": 2082,
                "bs_month": 11,
                "bs_day": 3,
                "gregorian_date": "2026-02-15",
                "source_file": "holidays_2082_matched.csv",
                "source_citation": "MoHA Public Holidays 2082 BS (OCR matched)",
                "override_match": False,
                "override_date": {"start": "2026-02-14", "source": "moha_pdf_2082"},
            }
        ],
    }

    summary = validate_ground_truth_payload(payload)

    assert summary["status"] == "ok"
    assert summary["gate_passed"] is True
    assert summary["declared_conflict_count"] == 1
    assert summary["authority_mismatch_count"] == 0


def test_validate_ground_truth_payload_flags_missing_source_lineage_and_unsupported_years():
    payload = {
        "_meta": {"bs_years": [2082]},
        "records": [
            {
                "festival_id": "dashain",
                "bs_year": 2083,
                "bs_month": 6,
                "bs_day": 1,
                "gregorian_date": "2026-09-17",
            }
        ],
    }

    summary = validate_ground_truth_payload(payload)

    assert summary["status"] == "error"
    assert summary["unsupported_year_count"] == 1
    assert summary["missing_source_lineage_count"] == 1
