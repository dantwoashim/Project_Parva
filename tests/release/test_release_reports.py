from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_route_proof_matrix_check_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/release/generate_route_proof_matrix.py", "--check"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_source_coverage_reports_are_current_and_bounded() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/release/generate_source_coverage_report.py", "--check"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    matrix = json.loads(Path("reports/source_coverage/coverage_matrix.json").read_text(encoding="utf-8"))
    assert matrix["not_authority"] is True
    assert any(row["operation"] == "panchanga_summary" for row in matrix["rows"])
    assert Path("reports/source_coverage/year_field_status.md").exists()
    assert Path("reports/source_coverage/panchanga_method_coverage.md").exists()


def test_jpl_lane_report_is_current_and_does_not_claim_fallback_jpl() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/release/check_jpl_lane.py", "--check"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(Path("reports/panchanga/jpl_lane_report.json").read_text(encoding="utf-8"))
    assert report["fallback_claims_jpl"] is False
    if report["status"] == "skipped":
        assert report["real_jpl_kernel_claimed"] is False


def test_external_reviewer_dry_audit_is_current() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/release/generate_external_review_dry_audit.py", "--check"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(Path("reports/external/reviewer_dry_audit.json").read_text(encoding="utf-8"))
    assert report["external_review_claimed"] is False
    assert report["missing"] == []
