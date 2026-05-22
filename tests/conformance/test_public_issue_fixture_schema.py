from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SUITE_DIR = ROOT / "conformance" / "public-nepali-date-issues"
SCHEMA_PATH = SUITE_DIR / "schema.json"

FAILURE_CLASSES = {
    "frontend_backend_source_drift",
    "month_length_mismatch",
    "year_total_mismatch",
    "bs_to_ad_conversion_mismatch",
    "ad_to_bs_conversion_mismatch",
    "roundtrip_mismatch",
    "invalid_bs_date_accepted",
    "unsupported_lower_range",
    "unsupported_upper_range",
    "future_bs_uncertainty",
    "fiscal_year_boundary",
    "payroll_date_risk",
    "holiday_working_day",
    "panchanga",
    "business_workflow_gap",
    "source_provenance",
    "other",
}

EVIDENCE_LEVELS = {
    "verified_public_issue",
    "reported_public_issue",
    "reported_public_issue_partial",
    "narrative_evidence",
    "business_wedge",
    "review_needed",
}

RECOMMENDED_ACTIONS = {
    "fixture_only",
    "upstream_comment",
    "upstream_pr_candidate",
    "business_evidence",
    "monitor",
    "manual_verification_required",
}

CONFIDENCE_LEVELS = {"high", "medium", "low", "needs_manual_verification"}

REQUIRED_CASE_FIELDS = {
    "id",
    "title",
    "source_project",
    "source_url",
    "source_issue_url",
    "source_pr_url",
    "source_commit",
    "failure_class",
    "evidence_level",
    "reported_input",
    "reported_expected",
    "reported_actual",
    "parva_expected",
    "executable",
    "runner_operation",
    "confidence",
    "authority_boundary",
    "safe_claim",
    "forbidden_claims",
    "recommended_action",
    "notes",
    "tags",
}

CASE_FILES = [
    "high_confidence_cases.json",
    "source_drift_cases.json",
    "month_length_cases.json",
    "conversion_cases.json",
    "invalid_date_cases.json",
    "range_boundary_cases.json",
    "future_uncertainty_cases.json",
    "business_workflow_cases.json",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _case_packs() -> list[tuple[Path, dict[str, Any]]]:
    return [(SUITE_DIR / name, _load(SUITE_DIR / name)) for name in CASE_FILES]


def test_public_issue_schema_and_fixture_files_exist() -> None:
    assert SCHEMA_PATH.exists()
    schema = _load(SCHEMA_PATH)
    assert schema["title"] == "Project Parva public Nepali date issue fixture pack"
    for filename in CASE_FILES:
        assert (SUITE_DIR / filename).exists(), filename


def test_public_issue_fixture_pack_shape() -> None:
    for path, payload in _case_packs():
        assert payload["suite"] == "public-nepali-date-issues", path
        assert isinstance(payload["version"], int)
        assert payload["description"]
        assert isinstance(payload["cases"], list)
        for case in payload["cases"]:
            assert REQUIRED_CASE_FIELDS <= set(case), case.get("id")
            assert case["failure_class"] in FAILURE_CLASSES
            assert case["evidence_level"] in EVIDENCE_LEVELS
            assert case["recommended_action"] in RECOMMENDED_ACTIONS
            assert case["confidence"] in CONFIDENCE_LEVELS
            assert isinstance(case["executable"], bool)
            assert isinstance(case["tags"], list)
            assert case["authority_boundary"].strip()
            assert case["safe_claim"].strip()
            assert isinstance(case["forbidden_claims"], list) and case["forbidden_claims"]


def test_public_issue_fixture_schema_rules() -> None:
    for _path, payload in _case_packs():
        for case in payload["cases"]:
            if case["executable"]:
                assert case["runner_operation"], case["id"]
            if case["evidence_level"] == "verified_public_issue":
                assert case["reported_input"] is not None, case["id"]
                assert case["reported_expected"] is not None or case["reported_actual"] is not None, case["id"]
            if case["evidence_level"] in {"narrative_evidence", "business_wedge"}:
                assert case["executable"] is False, case["id"]


def test_public_issue_case_ids_are_unique_in_executable_category_files() -> None:
    seen: set[str] = set()
    for path, payload in _case_packs():
        if payload.get("metadata_only"):
            continue
        for case in payload["cases"]:
            assert case["id"] not in seen, f"{case['id']} duplicated in {path}"
            seen.add(case["id"])


def test_expected_initial_evidence_set_is_represented() -> None:
    case_ids = {case["id"] for _path, payload in _case_packs() for case in payload["cases"]}
    expected = {
        "yarsa-257-258-2087-mangsir-source-drift",
        "leapfrog-70-2082-2083-month-length-cluster",
        "leapfrog-13-2018-03-12-range-error",
        "leapfrog-33-35-april-2021-boundary",
        "go-nepali-15-2024-06-14-ad-to-bs-boundary",
        "medic-bikram-sambat-26-2081-2082-month-corrections",
        "node-nepali-datetime-82-source-provenance",
        "node-nepali-datetime-121-future-date-accuracy",
        "cht-core-7925-invalid-kartik-2079-accepted",
        "odk-pre-1951-lower-bound-range",
        "subeshb1-71-upper-range-above-2090-12-30",
        "erpnext-31245-bs-support-request",
        "frappe-books-787-bs-support-request",
    }
    assert expected <= case_ids
