from __future__ import annotations

import csv
from pathlib import Path

from scripts.conformance.score_conformance import score_rows


def test_conformance_scoring_reaches_platinum_for_sample() -> None:
    sample = Path("samples/conformance/vendor_input_sample.csv")
    with sample.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    report = score_rows(rows)
    assert report["claim_boundary"] == "technical_conformance_report_not_certification"
    assert report["not_authority"] is True
    assert report["achieved_level"] == "platinum"


def test_missing_review_gate_blocks_gold() -> None:
    rows = [
        {"workflow_type": "bs_ad_conversion", "expected_behavior": "valid", "supported_range": "true"},
        {"workflow_type": "bs_ad_conversion", "expected_behavior": "invalid_date", "supported_range": "true"},
        {"workflow_type": "holiday", "institution_profile": "sample"},
    ]
    report = score_rows(rows)
    assert report["achieved_level"] == "bronze"
    assert "review_required_behavior" in report["levels"]["gold"]["missing_checks"]
