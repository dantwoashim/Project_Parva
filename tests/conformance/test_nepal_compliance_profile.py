from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = ROOT / "conformance" / "profiles" / "nepal-compliance.json"
DOC_PATH = ROOT / "docs" / "conformance" / "nepal-compliance-profile.md"
CASE_DIR = ROOT / "conformance" / "public-nepali-date-issues"


def _public_issue_case_ids() -> set[str]:
    case_ids: set[str] = set()
    for path in CASE_DIR.glob("*.json"):
        if path.name == "schema.json":
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("metadata_only"):
            continue
        for case in payload["cases"]:
            case_ids.add(case["id"])
    return case_ids


def test_nepal_compliance_profile_shape() -> None:
    assert PROFILE_PATH.exists()
    payload = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))

    assert payload["id"] == "nepal-compliance"
    assert payload["description"]
    assert payload["target_workflows"]
    assert payload["related_public_cases"]
    assert payload["checks"]
    assert payload["status"] == "public_conformance_profile_v1"


def test_nepal_compliance_profile_does_not_overclaim() -> None:
    text = PROFILE_PATH.read_text(encoding="utf-8") + "\n" + DOC_PATH.read_text(encoding="utf-8")
    forbidden = [
        "official truth",
        "Yarsa adopted Project Parva",
        "powers nepal-compliance",
        "guaranteed future",
        "official Nepali calendar authority",
    ]
    for phrase in forbidden:
        assert phrase not in text


def test_nepal_compliance_related_cases_exist() -> None:
    payload = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    missing = set(payload["related_public_cases"]) - _public_issue_case_ids()
    assert missing == set()


def test_nepal_compliance_profile_doc_exists() -> None:
    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")
    assert "py -3.11 tools\\conformance_runner\\run.py --profile nepal-compliance" in text


def test_nepal_compliance_profile_runner_command() -> None:
    result = subprocess.run(
        [sys.executable, "tools/conformance_runner/run.py", "--profile", "nepal-compliance"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Parva conformance profile summary" in result.stdout
    assert "profile: nepal-compliance" in result.stdout
