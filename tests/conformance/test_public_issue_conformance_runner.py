from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from tools.conformance_runner import run as conformance_run

ROOT = Path(__file__).resolve().parents[2]


def test_public_issue_runner_discovers_suite() -> None:
    summary = conformance_run.run_public_issue_suite(ROOT / "conformance")

    assert summary.total >= 22
    assert summary.executed >= 8
    assert summary.failed == 0
    assert summary.skipped >= 1
    assert summary.review_needed >= 5
    assert {result.case_id for result in summary.results} >= {
        "yarsa-257-258-2087-mangsir-source-drift",
        "go-nepali-15-2024-06-14-ad-to-bs-boundary",
        "cht-core-7925-invalid-kartik-2079-accepted",
        "medic-26-2081-11-month-length-correction",
        "medic-26-2082-03-month-length-correction",
        "medic-26-2082-04-month-length-correction",
        "medic-26-2082-10-month-length-correction",
    }


def test_public_issue_cli_summary_output() -> None:
    result = subprocess.run(
        [sys.executable, "tools/conformance_runner/run.py", "--suite", "public-nepali-date-issues"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Parva public issue conformance summary" in result.stdout
    assert "total: 24" in result.stdout
    assert "executed: 14" in result.stdout
    assert "failed: 0" in result.stdout


def test_public_issue_runner_fails_on_malformed_fixture_copy(tmp_path: Path) -> None:
    case_root = tmp_path / "conformance"
    shutil.copytree(ROOT / "conformance" / "public-nepali-date-issues", case_root / "public-nepali-date-issues")
    target = case_root / "public-nepali-date-issues" / "conversion_cases.json"
    payload = json.loads(target.read_text(encoding="utf-8"))
    payload["cases"][0].pop("authority_boundary")
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    summary = conformance_run.run_public_issue_suite(case_root)

    assert summary.failed == 1
    failed = [result for result in summary.results if not result.passed]
    assert "missing required keys" in failed[0].message


def test_public_issue_runner_rejects_duplicate_ids(tmp_path: Path) -> None:
    case_root = tmp_path / "conformance"
    shutil.copytree(ROOT / "conformance" / "public-nepali-date-issues", case_root / "public-nepali-date-issues")
    target = case_root / "public-nepali-date-issues" / "conversion_cases.json"
    payload = json.loads(target.read_text(encoding="utf-8"))
    payload["cases"][1]["id"] = payload["cases"][0]["id"]
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    summary = conformance_run.run_public_issue_suite(case_root)

    assert summary.failed == 1
    failed = [result for result in summary.results if not result.passed]
    assert "duplicate public issue case id" in failed[0].message
