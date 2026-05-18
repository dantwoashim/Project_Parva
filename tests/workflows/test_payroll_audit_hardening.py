from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

from app.workflows.date_risk_audit import (
    audit_date_rows,
    build_date_risk_timepack,
    verify_date_risk_timepack,
)


def _rows(path: str) -> list[dict[str, str]]:
    return list(csv.DictReader(Path(path).read_text(encoding="utf-8").splitlines()))


def test_payroll_audit_handles_malformed_spreadsheet_rows() -> None:
    findings = audit_date_rows(_rows("examples/payroll/ugly.csv"), include_proofs=True)
    by_employee = {item["original_row"].get("employee_id"): item for item in findings}

    assert by_employee["E-001"]["status"] == "pass"
    assert "missing_bs_date" in by_employee["E-002"]["issues"]
    assert {"invalid_bs_date", "invalid_ad_date"}.issubset(by_employee["E-003"]["issues"])
    assert {"holiday_conflict", "non_working_day_conflict", "static_reference_overclaim", "authority_overclaim"}.issubset(
        by_employee["E-004"]["issues"]
    )
    assert "fiscal_boundary_ambiguity" in by_employee["E-005"]["issues"]
    assert "review_required_future_sensitive" in by_employee["E-006"]["issues"]
    assert findings[-1]["issues"].count("duplicate_row") == 1
    assert all("row_number" in item and "original_row" in item for item in findings)
    assert all(item["claim_boundary"] == "payroll_date_risk_not_authority" for item in findings)


def test_payroll_timepack_from_ugly_rows_verifies() -> None:
    timepack = build_date_risk_timepack(_rows("examples/payroll/ugly.csv"))
    ok, reason = verify_date_risk_timepack(timepack)

    assert ok, reason
    assert timepack["boundary_summary"]["not_authority"] is True
    assert timepack["result_summary"]["review_required"] >= 1


def test_payroll_cli_outputs_json_markdown_and_timepack(tmp_path: Path) -> None:
    json_out = tmp_path / "report.json"
    md_out = tmp_path / "report.md"
    timepack_out = tmp_path / "report.timepack.json"
    command = [
        sys.executable,
        "-m",
        "parva.cli",
        "audit",
        "payroll",
        "--input",
        "examples/payroll/ugly.csv",
        "--output",
        str(json_out),
        "--markdown",
        str(md_out),
        "--timepack",
        str(timepack_out),
    ]
    pythonpath = os.pathsep.join(
        [
            str(Path("packages/parva-python")),
            str(Path("backend")),
            str(Path(".")),
            os.environ.get("PYTHONPATH", ""),
        ]
    )
    result = subprocess.run(
        command,
        cwd=Path.cwd(),
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "PYTHONPATH": pythonpath},
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(json_out.read_text(encoding="utf-8"))
    assert report["not_authority"] is True
    assert report["summary"]["review_required"] >= 1
    assert "not legal, tax, payroll, banking, government" in md_out.read_text(encoding="utf-8")
    ok, reason = verify_date_risk_timepack(json.loads(timepack_out.read_text(encoding="utf-8")))
    assert ok, reason
