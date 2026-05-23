from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.conformance_runner import run as conformance_run

ROOT = Path(__file__).resolve().parents[2]


def test_public_issue_report_generation(tmp_path: Path) -> None:
    report_path = tmp_path / "public-issue-suite-summary.json"
    result = subprocess.run(
        [
            sys.executable,
            "tools/conformance_runner/run.py",
            "--suite",
            "public-nepali-date-issues",
            "--write-report",
            str(report_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert report_path.exists()
    md_path = report_path.with_suffix(".md")
    assert md_path.exists()

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    summary = conformance_run.run_public_issue_suite(ROOT / "conformance")

    assert payload["suite"] == "public-nepali-date-issues"
    assert payload["summary"] == {
        "total_cases": summary.total,
        "executed": summary.executed,
        "passed": summary.passed,
        "failed": summary.failed,
        "skipped": summary.skipped,
        "review_needed": summary.review_needed,
    }
    assert len(payload["executable_case_ids"]) == summary.executed
    assert len(payload["skipped_case_ids"]) == summary.skipped
    assert payload["failure_class_counts"]["month_length_mismatch"] >= 1
    assert payload["evidence_level_counts"]["verified_public_issue"] >= 1
    assert payload["authority_boundary"]
    assert payload["safe_claim"]
    assert payload["no_official_authority_statement"]

    markdown = md_path.read_text(encoding="utf-8")
    for heading in [
        "# Public Nepali Date Issue Conformance Summary",
        "## Summary",
        "## Executed Cases",
        "## Skipped/documented Cases",
        "## Review-needed Cases",
        "## Failure-class Breakdown",
        "## Evidence-level Breakdown",
        "## Authority Boundary",
    ]:
        assert heading in markdown

    forbidden = [
        "official " + "truth",
        "infrastructural " + "superiority",
        "must adopt " + "Parva",
        "adopted " + "Project Parva",
        "powers " + "nepal-compliance",
        "guaranteed " + "future",
        "catast" + "rophic",
        "official Nepali calendar " + "authority",
    ]
    report_text = json.dumps(payload, ensure_ascii=False) + "\n" + markdown
    for phrase in forbidden:
        assert phrase not in report_text
