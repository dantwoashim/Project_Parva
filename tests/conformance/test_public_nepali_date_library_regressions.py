from __future__ import annotations

import json
from pathlib import Path

from tools.conformance_runner import run as conformance_run

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = (
    ROOT
    / "conformance"
    / "public-nepali-date-libraries"
    / "leapfrog_nepali_date_picker_2082_2083_cases.json"
)


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_leapfrog_public_regression_fixture_schema_and_boundaries() -> None:
    payload = _fixture()

    assert payload["source_project"] == "leapfrogtechnology/nepali-date-picker"
    assert payload["authority_boundary"] == "public_issue_regression_case_not_official_authority"
    assert {summary["issue"] for summary in payload["issue_summaries"]} == {66, 68, 69, 70}
    assert payload["cases"]

    forbidden_fragments = [
        "official " + "truth",
        "production impact",
        "Leapfrog is " + "broken",
    ]
    text = json.dumps(payload, ensure_ascii=False)
    for fragment in forbidden_fragments:
        assert fragment not in text

    for case in payload["cases"]:
        assert case["operation"] == "public_nepali_date_library_regression"
        assert case["source_project"] == payload["source_project"]
        assert case["source_url"] == payload["source_url"]
        assert case["publication_status"] == "needs_review"
        assert case["source_policy"] == "public_issue_regression_case"
        assert case["authority_boundary"] == "public_issue_regression_case_not_official_authority"
        assert case["production_impact_claimed"] is False
        assert case["expected"]["observed_current_source"]["reproduction_status"].startswith("still_reproduces")
        assert "parva" in case["expected"]


def test_issue_70_month_day_cases_are_represented() -> None:
    cases = _fixture()["cases"]
    issue_70_cases = [case for case in cases if case["source_issue"] == 70]

    assert len(issue_70_cases) == 12
    represented = {(case["input"]["bs_year"], case["input"]["bs_month"]) for case in issue_70_cases}
    assert represented == {
        (2082, 1),
        (2082, 2),
        (2082, 3),
        (2082, 4),
        (2082, 6),
        (2082, 8),
        (2082, 9),
        (2082, 10),
        (2083, 6),
        (2083, 8),
        (2083, 9),
        (2083, 10),
    }

    review_rows = [case for case in issue_70_cases if not case["expected"]["parva"]["matches_issue_reported"]]
    assert {case["input"]["bs_month_name"] for case in review_rows} == {"Asar", "Shrawan"}


def test_public_regression_cases_are_loaded_by_conformance_runner() -> None:
    failures, results = conformance_run.run(ROOT / "conformance")

    assert failures == 0
    case_ids = {result.case_id for result in results}
    assert "leapfrog-issue-70-2082-mangsir-month-days" in case_ids
    assert "leapfrog-issue-69-2025-05-19-ad-to-bs" in case_ids
