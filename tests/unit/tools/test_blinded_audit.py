from __future__ import annotations

import csv
import json
from pathlib import Path

from tools.future_bs_audit.blinded_audit import run_blinded_audit

ROOT = Path(__file__).resolve().parents[3]
SAMPLE = ROOT / "tools" / "future_bs_audit" / "sample_external_sheet.synthetic.csv"


def test_blinded_audit_output_is_aggregate_only_by_default():
    report = run_blinded_audit(SAMPLE)
    serialized = json.dumps(report)

    assert report["publication_status"] == "computed_prediction_not_official"
    assert report["total_months_checked"] == 24
    assert report["corrected_values_included"] is False
    assert report["agreement_count"] + report["disagreement_count"] == report["total_months_checked"]
    assert "corrected_value" not in serialized.replace("corrected_values_included", "")
    assert "predicted_days" not in serialized
    assert "month_results" not in serialized
    assert "rows" not in report


def test_synthetic_sample_contains_no_private_future_values():
    text = SAMPLE.read_text(encoding="utf-8")
    for forbidden in ["2084", "2099", "2200"]:
        assert forbidden not in text

    with SAMPLE.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert {row["bs_year"] for row in rows} == {"9000", "9001"}
    assert all(1 <= int(row["bs_month"]) <= 12 for row in rows)
    assert all(29 <= int(row["month_length"]) <= 32 for row in rows)


def test_corrected_values_included_false_by_default():
    report = run_blinded_audit(SAMPLE)

    assert report["corrected_values_included"] is False
    assert "agreement_definition" in report
    assert report["agreement_definition"].endswith("not_a_private_value_match")
