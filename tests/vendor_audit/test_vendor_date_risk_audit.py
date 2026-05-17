from __future__ import annotations

import json
from pathlib import Path

from scripts.vendor_audit.run_vendor_date_risk_audit import run_audit


def test_vendor_date_risk_audit_generates_json_and_markdown(tmp_path: Path) -> None:
    csv_path = tmp_path / "input.csv"
    json_out = tmp_path / "report.json"
    md_out = tmp_path / "report.md"
    csv_path.write_text(
        "\n".join(
            [
                "bs_date,workflow_type,expected_behavior,actual_ad_date,holiday_assumption,fiscal_assumption",
                "2082-01-01,invoice_due_date,next_working_day,2025-04-14,known_public_holidays,nepal_fiscal_year",
                "2082-13-01,payroll_cutoff,reject_invalid_date,,known_public_holidays,nepal_fiscal_year",
                "2090-01-01,loan_repayment,review_required,,unknown_future_holiday_policy,nepal_fiscal_year",
            ]
        ),
        encoding="utf-8",
    )

    report = run_audit(csv_path, json_out, md_out)

    assert json_out.exists()
    assert md_out.exists()
    assert report["summary"]["not_authority"] is True
    assert report["invalid_dates"]
    assert report["review_required_cases"]
    assert report["unsupported_future_assumptions"]
    assert "technical conformance report" in md_out.read_text(encoding="utf-8")
    assert json.loads(json_out.read_text(encoding="utf-8"))["summary"]["rows"] == 3
