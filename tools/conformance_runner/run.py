#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

CASE_FILES = [
    "conversion/bs_to_ad_cases.json",
    "conversion/ad_to_bs_cases.json",
    "conversion/round_trip_cases.json",
    "validation/invalid_bs_dates.json",
    "fiscal/fiscal_boundary_cases.json",
    "release/release_manifest_cases.json",
    "future-risk-shape/public_safe_cases.json",
    "panchanga-shape/public_safe_shape_cases.json",
    "public-nepali-date-libraries/leapfrog_nepali_date_picker_2082_2083_cases.json",
]

PUBLIC_ISSUE_CASE_FILES = [
    "source_drift_cases.json",
    "month_length_cases.json",
    "conversion_cases.json",
    "invalid_date_cases.json",
    "range_boundary_cases.json",
    "future_uncertainty_cases.json",
    "business_workflow_cases.json",
]

PROFILE_DIR = ROOT / "conformance" / "profiles"

PUBLICATION_STATUSES = {
    "official_verified",
    "printed_verified",
    "public_witness",
    "publisher_reference",
    "software_table_reference",
    "third_party_reference",
    "needs_review",
    "computed_prediction_not_official",
}

RISK_LABELS = {"GREEN", "YELLOW", "RED"}

PUBLIC_ISSUE_FAILURE_CLASSES = {
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

PUBLIC_ISSUE_EVIDENCE_LEVELS = {
    "verified_public_issue",
    "reported_public_issue",
    "reported_public_issue_partial",
    "narrative_evidence",
    "business_wedge",
    "review_needed",
}

PUBLIC_ISSUE_RECOMMENDED_ACTIONS = {
    "fixture_only",
    "upstream_comment",
    "upstream_pr_candidate",
    "business_evidence",
    "monitor",
    "manual_verification_required",
}

FORBIDDEN_PUBLIC_KEYS = {
    "predicted" + "_days",
    "month" + "_length",
    "corrected" + "_value",
    "month" + "_lengths",
    "months",
}

FORBIDDEN_TEXT_PATTERNS = [
    re.compile("Info" + r"Developers", re.IGNORECASE),
    re.compile(r"\b" + "info" + r"dev\b", re.IGNORECASE),
    re.compile("cracked" + r"\s+Panchanga", re.IGNORECASE),
    re.compile("99%" + r"\s+future\s+accuracy", re.IGNORECASE),
]


@dataclass
class CaseResult:
    case_id: str
    passed: bool
    message: str
    file: str


class ConformanceError(ValueError):
    pass


@dataclass
class PublicIssueSummary:
    total: int
    executed: int
    passed: int
    failed: int
    skipped: int
    review_needed: int
    results: list[CaseResult]


def _load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ConformanceError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ConformanceError(f"{path}: root must be an object")
    return payload


def _case_value(case: dict[str, Any], key: str) -> Any:
    value = case.get(key)
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ConformanceError(f"{case.get('id', '<unknown>')}: {key} must be an object or null")
    return value


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _require_keys(mapping: dict[str, Any], keys: list[str], context: str) -> None:
    missing = [key for key in keys if key not in mapping]
    if missing:
        raise ConformanceError(f"{context}: missing required keys: {', '.join(missing)}")


def _assert_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise ConformanceError(f"{label}: expected {expected!r}, got {actual!r}")


def _assert_no_forbidden_text(path: Path, payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False)
    for pattern in FORBIDDEN_TEXT_PATTERNS:
        if pattern.search(text):
            raise ConformanceError(f"{path}: forbidden public-safety text matched {pattern.pattern}")


def _assert_no_forbidden_keys(mapping: Any, context: str) -> None:
    if isinstance(mapping, dict):
        for key, value in mapping.items():
            if key in FORBIDDEN_PUBLIC_KEYS:
                raise ConformanceError(f"{context}: forbidden future-sensitive key {key!r}")
            _assert_no_forbidden_keys(value, f"{context}.{key}")
    elif isinstance(mapping, list):
        for index, value in enumerate(mapping):
            _assert_no_forbidden_keys(value, f"{context}[{index}]")


def _validate_case_shape(case: dict[str, Any], path: Path, index: int) -> None:
    context = f"{_display_path(path)} cases[{index}]"
    _require_keys(
        case,
        ["case_id", "operation", "input", "expected", "source_policy", "publication_status"],
        context,
    )
    if case["publication_status"] not in PUBLICATION_STATUSES:
        raise ConformanceError(f"{context}: invalid publication_status {case['publication_status']!r}")
    if not isinstance(case["input"], dict) or not isinstance(case["expected"], dict):
        raise ConformanceError(f"{context}: input and expected must be objects")
    if case["operation"] == "future_risk_shape":
        _assert_equal(
            case["publication_status"],
            "computed_prediction_not_official",
            f"{context}.publication_status",
        )
        _assert_no_forbidden_keys(case["input"], context)


def _parse_bs_string(value: str) -> tuple[int, int, int]:
    try:
        year_raw, month_raw, day_raw = value.split("-")
        if len(year_raw) != 4 or len(month_raw) != 2 or len(day_raw) != 2:
            raise ValueError
        return int(year_raw), int(month_raw), int(day_raw)
    except (AttributeError, ValueError) as exc:
        raise ConformanceError(f"Malformed BS date string: {value!r}") from exc


def _run_local_case(case: dict[str, Any]) -> None:
    from app.calendar.bikram_sambat import bs_to_gregorian, gregorian_to_bs, is_valid_bs_date
    from app.calendar.panchanga import get_panchanga
    from app.services.enterprise_calendar_service import fiscal_year_payload

    operation = case["operation"]
    input_payload = case["input"]
    expected = case["expected"]

    if operation == "bs_to_ad":
        actual = bs_to_gregorian(
            int(input_payload["year"]),
            int(input_payload["month"]),
            int(input_payload["day"]),
        ).isoformat()
        _assert_equal(actual, expected["date"], case["case_id"])
        return

    if operation == "ad_to_bs":
        bs_year, bs_month, bs_day = gregorian_to_bs(date.fromisoformat(input_payload["date"]))
        _assert_equal(
            {"year": bs_year, "month": bs_month, "day": bs_day},
            {key: expected[key] for key in ["year", "month", "day"]},
            case["case_id"],
        )
        return

    if operation == "round_trip_bs_ad_bs":
        ad_date = bs_to_gregorian(
            int(input_payload["year"]),
            int(input_payload["month"]),
            int(input_payload["day"]),
        )
        bs_year, bs_month, bs_day = gregorian_to_bs(ad_date)
        _assert_equal(
            {"year": bs_year, "month": bs_month, "day": bs_day},
            {key: expected[key] for key in ["year", "month", "day"]},
            case["case_id"],
        )
        return

    if operation == "round_trip_ad_bs_ad":
        bs_tuple = gregorian_to_bs(date.fromisoformat(input_payload["date"]))
        actual = bs_to_gregorian(*bs_tuple).isoformat()
        _assert_equal(actual, expected["date"], case["case_id"])
        return

    if operation == "validate_bs_date":
        valid = is_valid_bs_date(
            int(input_payload["year"]),
            int(input_payload["month"]),
            int(input_payload["day"]),
        )
        _assert_equal(valid, expected["valid"], case["case_id"])
        return

    if operation == "validate_bs_date_string":
        try:
            _parse_bs_string(str(input_payload["value"]))
            valid = True
        except ConformanceError:
            valid = False
        _assert_equal(valid, expected["valid"], case["case_id"])
        return

    if operation == "fiscal_year_boundary":
        payload = fiscal_year_payload(int(input_payload["fiscal_year_start"]))
        actual = {
            "label": payload["fiscal_year"],
            "start_bs": payload["start"]["bs"],
            "start_ad": payload["start"]["ad"],
            "end_bs": payload["end"]["bs"],
            "end_ad": payload["end"]["ad"],
        }
        _assert_equal(actual, expected, case["case_id"])
        return

    if operation == "release_manifest_shape":
        for field in expected["required_fields"]:
            if field not in input_payload:
                raise ConformanceError(f"{case['case_id']}: release manifest missing {field}")
        return

    if operation == "future_risk_shape":
        _assert_equal(
            input_payload.get("publication_status"),
            "computed_prediction_not_official",
            f"{case['case_id']}.publication_status",
        )
        _assert_equal(
            input_payload.get("corrected_value_included"),
            False,
            f"{case['case_id']}.corrected_value_included",
        )
        if input_payload.get("risk_label") not in RISK_LABELS:
            raise ConformanceError(f"{case['case_id']}: risk_label missing or invalid")
        if expected.get("sensitive_value_fields_absent") is True:
            _assert_no_forbidden_keys(input_payload, case["case_id"])
        return

    if operation == "panchanga_shape":
        payload = get_panchanga(date.fromisoformat(input_payload["date"]))
        for field in expected["required_fields"]:
            if field not in payload:
                raise ConformanceError(f"{case['case_id']}: panchanga missing {field}")
        for parent, fields in expected.get("nested_required", {}).items():
            node = payload.get(parent)
            if not isinstance(node, dict):
                raise ConformanceError(f"{case['case_id']}: panchanga {parent} must be object")
            for field in fields:
                if field not in node:
                    raise ConformanceError(f"{case['case_id']}: panchanga {parent}.{field} missing")
        return

    if operation == "public_nepali_date_library_regression":
        from app.calendar.bikram_sambat import days_in_bs_month

        if case.get("authority_boundary") != "public_issue_regression_case_not_official_authority":
            raise ConformanceError(f"{case['case_id']}: public issue boundary missing")
        if case.get("production_impact_claimed") is not False:
            raise ConformanceError(f"{case['case_id']}: production impact must not be claimed")

        check = input_payload.get("check")
        parva_expected = expected.get("parva")
        if not isinstance(parva_expected, dict):
            raise ConformanceError(f"{case['case_id']}: parva expected behavior missing")

        if check == "month_days":
            actual = days_in_bs_month(int(input_payload["bs_year"]), int(input_payload["bs_month"]))
            _assert_equal(actual, parva_expected["month_days"], case["case_id"])
            return

        if check == "ad_to_bs":
            bs_year, bs_month, bs_day = gregorian_to_bs(date.fromisoformat(str(input_payload["ad_date"])))
            actual = {"year": bs_year, "month": bs_month, "day": bs_day}
            _assert_equal(actual, parva_expected["bs_date"], case["case_id"])
            return

        raise ConformanceError(f"{case['case_id']}: unsupported public library regression check {check!r}")

    raise ConformanceError(f"{case['case_id']}: unsupported operation {operation!r}")


def _validate_public_issue_case(case: dict[str, Any], path: Path, index: int) -> None:
    context = f"{_display_path(path)} cases[{index}]"
    required = [
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
    ]
    _require_keys(case, required, context)
    if case["failure_class"] not in PUBLIC_ISSUE_FAILURE_CLASSES:
        raise ConformanceError(f"{context}: invalid failure_class {case['failure_class']!r}")
    if case["evidence_level"] not in PUBLIC_ISSUE_EVIDENCE_LEVELS:
        raise ConformanceError(f"{context}: invalid evidence_level {case['evidence_level']!r}")
    if case["recommended_action"] not in PUBLIC_ISSUE_RECOMMENDED_ACTIONS:
        raise ConformanceError(f"{context}: invalid recommended_action {case['recommended_action']!r}")
    if case["confidence"] not in {"high", "medium", "low", "needs_manual_verification"}:
        raise ConformanceError(f"{context}: invalid confidence {case['confidence']!r}")
    if not isinstance(case["executable"], bool):
        raise ConformanceError(f"{context}: executable must be boolean")
    if case["executable"] and not case["runner_operation"]:
        raise ConformanceError(f"{context}: executable cases require runner_operation")
    if case["evidence_level"] == "verified_public_issue":
        if case["reported_input"] is None:
            raise ConformanceError(f"{context}: verified_public_issue requires reported_input")
        if case["reported_expected"] is None and case["reported_actual"] is None:
            raise ConformanceError(
                f"{context}: verified_public_issue requires reported_expected or reported_actual"
            )
    if not str(case["authority_boundary"]).strip():
        raise ConformanceError(f"{context}: authority_boundary must be non-empty")
    if not str(case["safe_claim"]).strip():
        raise ConformanceError(f"{context}: safe_claim must be non-empty")
    forbidden_claims = case["forbidden_claims"]
    if not isinstance(forbidden_claims, list) or not forbidden_claims:
        raise ConformanceError(f"{context}: forbidden_claims must be a non-empty array")
    if not isinstance(case["tags"], list):
        raise ConformanceError(f"{context}: tags must be an array")


def _run_public_issue_case(case: dict[str, Any]) -> None:
    from app.calendar.bikram_sambat import days_in_bs_month, gregorian_to_bs, is_valid_bs_date

    operation = case["runner_operation"]
    reported_input = _case_value(case, "reported_input")
    parva_expected = _case_value(case, "parva_expected")

    if operation == "documented_only":
        return

    if operation == "source_drift":
        reported_expected = _case_value(case, "reported_expected")
        reported_actual = _case_value(case, "reported_actual")
        for key in ("backend_month_days", "frontend_month_days"):
            if key not in reported_actual:
                raise ConformanceError(f"{case['id']}: source_drift missing {key}")
        if reported_actual["backend_month_days"] == reported_actual["frontend_month_days"]:
            raise ConformanceError(f"{case['id']}: source_drift case does not contain a drift")
        if reported_expected and "shift_examples" in reported_expected:
            for example in reported_expected["shift_examples"]:
                if example.get("backend_ad") == example.get("frontend_ad"):
                    raise ConformanceError(f"{case['id']}: shift example has no date shift")
        return

    if operation == "month_length":
        actual = days_in_bs_month(int(reported_input["bs_year"]), int(reported_input["bs_month"]))
        _assert_equal(actual, parva_expected["month_days"], case["id"])
        return

    if operation == "ad_to_bs":
        bs_year, bs_month, bs_day = gregorian_to_bs(date.fromisoformat(str(reported_input["ad_date"])))
        _assert_equal(
            {"year": bs_year, "month": bs_month, "day": bs_day},
            parva_expected["bs_date"],
            case["id"],
        )
        return

    if operation == "validate_bs_date":
        bs_date = reported_input["bs_date"]
        actual = is_valid_bs_date(int(bs_date["year"]), int(bs_date["month"]), int(bs_date["day"]))
        _assert_equal(actual, parva_expected["valid"], case["id"])
        return

    if operation == "range_boundary":
        expected_state = parva_expected.get("state")
        if expected_state not in {"unsupported_lower_range", "unsupported_upper_range", "review_needed"}:
            raise ConformanceError(f"{case['id']}: unsupported range_boundary state {expected_state!r}")
        return

    raise ConformanceError(f"{case['id']}: unsupported public issue runner_operation {operation!r}")


def _api_json(base_url: str, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
    url = base_url.rstrip("/") + path
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ConformanceError(f"API request failed for {url}: {exc}") from exc


def _run_api_case(case: dict[str, Any], base_url: str) -> None:
    operation = case["operation"]
    input_payload = case["input"]
    expected = case["expected"]

    if operation == "ad_to_bs":
        query = urllib.parse.urlencode({"date": input_payload["date"]})
        body = _api_json(base_url, "GET", f"/v3/api/calendar/convert?{query}")
        bs = body.get("bikram_sambat", {})
        actual = {"year": bs.get("year"), "month": bs.get("month"), "day": bs.get("day")}
        _assert_equal(actual, expected, case["case_id"])
        return

    if operation == "bs_to_ad":
        body = _api_json(base_url, "POST", "/v3/api/calendar/bs-to-gregorian", input_payload)
        actual = body.get("gregorian") or body.get("date")
        _assert_equal(actual, expected["date"], case["case_id"])
        return


def _load_case_files(case_root: Path) -> list[tuple[Path, dict[str, Any]]]:
    loaded: list[tuple[Path, dict[str, Any]]] = []
    for relative in CASE_FILES:
        path = case_root / relative
        if not path.exists():
            raise ConformanceError(f"missing required case file: {path}")
        payload = _load_json(path)
        _require_keys(payload, ["version", "case_set", "cases"], _display_path(path))
        if not isinstance(payload["cases"], list) or not payload["cases"]:
            raise ConformanceError(f"{path}: cases must be a non-empty array")
        _assert_no_forbidden_text(path, payload)
        loaded.append((path, payload))
    return loaded


def _load_public_issue_files(case_root: Path) -> list[tuple[Path, dict[str, Any]]]:
    suite_root = case_root / "public-nepali-date-issues"
    loaded: list[tuple[Path, dict[str, Any]]] = []
    for relative in PUBLIC_ISSUE_CASE_FILES:
        path = suite_root / relative
        if not path.exists():
            raise ConformanceError(f"missing public issue case file: {path}")
        payload = _load_json(path)
        _require_keys(payload, ["suite", "version", "description", "cases"], _display_path(path))
        if payload["suite"] != "public-nepali-date-issues":
            raise ConformanceError(f"{_display_path(path)}: suite must be public-nepali-date-issues")
        if not isinstance(payload["cases"], list):
            raise ConformanceError(f"{_display_path(path)}: cases must be an array")
        _assert_no_forbidden_text(path, payload)
        loaded.append((path, payload))
    return loaded


def run(case_root: Path, *, api_base_url: str | None = None) -> tuple[int, list[CaseResult]]:
    results: list[CaseResult] = []
    loaded = _load_case_files(case_root)
    for path, payload in loaded:
        for index, case in enumerate(payload["cases"]):
            case_id = str(case.get("case_id") or f"{path.name}:{index}")
            try:
                _validate_case_shape(case, path, index)
                _run_local_case(case)
                if api_base_url and case["operation"] in {"ad_to_bs", "bs_to_ad"}:
                    _run_api_case(case, api_base_url)
                results.append(CaseResult(case_id, True, "passed", _display_path(path)))
            except Exception as exc:  # noqa: BLE001
                results.append(CaseResult(case_id, False, str(exc), _display_path(path)))
    failures = sum(1 for result in results if not result.passed)
    return failures, results


def run_public_issue_suite(case_root: Path, case_ids: set[str] | None = None) -> PublicIssueSummary:
    results: list[CaseResult] = []
    loaded = _load_public_issue_files(case_root)
    seen_ids: set[str] = set()
    review_needed = 0
    for path, payload in loaded:
        for index, case in enumerate(payload["cases"]):
            case_id = str(case.get("id") or f"{path.name}:{index}")
            if case_ids is not None and case_id not in case_ids:
                continue
            try:
                _validate_public_issue_case(case, path, index)
                if case_id in seen_ids:
                    raise ConformanceError(f"duplicate public issue case id: {case_id}")
                seen_ids.add(case_id)
                if case["confidence"] == "needs_manual_verification" or case["evidence_level"] in {
                    "reported_public_issue_partial",
                    "review_needed",
                }:
                    review_needed += 1
                if not case["executable"]:
                    results.append(CaseResult(case_id, True, "skipped: documented-only public issue", _display_path(path)))
                    continue
                _run_public_issue_case(case)
                results.append(CaseResult(case_id, True, "passed", _display_path(path)))
            except Exception as exc:  # noqa: BLE001
                results.append(CaseResult(case_id, False, str(exc), _display_path(path)))
    failed = sum(1 for result in results if not result.passed)
    skipped = sum(1 for result in results if result.message.startswith("skipped:"))
    executed = len(results) - skipped
    passed = executed - failed
    return PublicIssueSummary(
        total=len(results),
        executed=executed,
        passed=passed,
        failed=failed,
        skipped=skipped,
        review_needed=review_needed,
        results=results,
    )


def _load_profile(profile_name: str) -> dict[str, Any]:
    path = PROFILE_DIR / f"{profile_name}.json"
    payload = _load_json(path)
    _require_keys(
        payload,
        [
            "id",
            "description",
            "target_workflows",
            "related_public_cases",
            "checks",
            "authority_boundary",
            "status",
        ],
        _display_path(path),
    )
    if payload["id"] != profile_name:
        raise ConformanceError(f"{_display_path(path)}: profile id must be {profile_name!r}")
    if not isinstance(payload["related_public_cases"], list) or not payload["related_public_cases"]:
        raise ConformanceError(f"{_display_path(path)}: related_public_cases must be non-empty")
    if not str(payload["authority_boundary"]).strip():
        raise ConformanceError(f"{_display_path(path)}: authority_boundary must be non-empty")
    return payload


def run_profile(profile_name: str, case_root: Path) -> tuple[dict[str, Any], PublicIssueSummary]:
    profile = _load_profile(profile_name)
    case_ids = {str(case_id) for case_id in profile["related_public_cases"]}
    summary = run_public_issue_suite(case_root, case_ids=case_ids)
    missing = case_ids - {result.case_id for result in summary.results}
    if missing:
        raise ConformanceError(
            f"profile {profile_name!r} references unknown public issue cases: {', '.join(sorted(missing))}"
        )
    return profile, summary


def _git_commit() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    commit = result.stdout.strip()
    return commit or None


def _public_issue_cases_by_id(
    case_root: Path,
    case_ids: set[str] | None = None,
) -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}
    for _path, payload in _load_public_issue_files(case_root):
        for case in payload["cases"]:
            case_id = str(case["id"])
            if case_ids is not None and case_id not in case_ids:
                continue
            cases[case_id] = case
    return cases


def _public_issue_report(
    summary: PublicIssueSummary,
    case_root: Path,
    *,
    suite_name: str,
    case_ids: set[str] | None = None,
) -> dict[str, Any]:
    cases_by_id = _public_issue_cases_by_id(case_root, case_ids=case_ids)
    result_by_id = {result.case_id: result for result in summary.results}

    executable_case_ids = sorted(
        case_id
        for case_id, case in cases_by_id.items()
        if case.get("executable") and case_id in result_by_id
    )
    skipped_case_ids = [
        {
            "case_id": result.case_id,
            "reason": result.message.removeprefix("skipped: ").strip(),
        }
        for result in summary.results
        if result.message.startswith("skipped:")
    ]
    review_needed_case_ids = sorted(
        case_id
        for case_id, case in cases_by_id.items()
        if case_id in result_by_id
        and (
            case.get("confidence") == "needs_manual_verification"
            or case.get("evidence_level") in {"reported_public_issue_partial", "review_needed"}
        )
    )

    failure_class_counts = Counter(str(case.get("failure_class")) for case in cases_by_id.values())
    evidence_level_counts = Counter(str(case.get("evidence_level")) for case in cases_by_id.values())

    return {
        "suite": suite_name,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "repository_commit": _git_commit(),
        "summary": {
            "total_cases": summary.total,
            "executed": summary.executed,
            "passed": summary.passed,
            "failed": summary.failed,
            "skipped": summary.skipped,
            "review_needed": summary.review_needed,
        },
        "executable_case_ids": executable_case_ids,
        "skipped_case_ids": skipped_case_ids,
        "review_needed_case_ids": review_needed_case_ids,
        "failure_class_counts": dict(sorted(failure_class_counts.items())),
        "evidence_level_counts": dict(sorted(evidence_level_counts.items())),
        "results": [
            {
                "case_id": result.case_id,
                "status": "passed"
                if result.passed and not result.message.startswith("skipped:")
                else "skipped"
                if result.message.startswith("skipped:")
                else "failed",
                "message": result.message,
                "case_file": result.file,
            }
            for result in summary.results
        ],
        "authority_boundary": "Public issue fixtures are regression and conformance evidence, not official calendar source material or upstream approval.",
        "safe_claim": "Project Parva runs a public Nepali date issue conformance suite with explicit evidence levels and review-needed boundaries.",
        "no_official_authority_statement": "This report is not a legal, payroll, banking, ritual, or calendar-publication authority.",
    }


def _write_public_issue_report(report: dict[str, Any], json_path: Path) -> tuple[Path, Path]:
    json_path = json_path if json_path.is_absolute() else ROOT / json_path
    md_path = json_path.with_suffix(".md")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(_public_issue_report_markdown(report), encoding="utf-8")
    return json_path, md_path


def _public_issue_report_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Public Nepali Date Issue Conformance Summary",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|---|---:|",
        f"| Total cases | {summary['total_cases']} |",
        f"| Executed | {summary['executed']} |",
        f"| Passed | {summary['passed']} |",
        f"| Failed | {summary['failed']} |",
        f"| Skipped/documented | {summary['skipped']} |",
        f"| Review-needed | {summary['review_needed']} |",
        "",
        f"- Suite: `{report['suite']}`",
        f"- Generated at: `{report['generated_at']}`",
        f"- Repository commit: `{report.get('repository_commit') or 'unknown'}`",
        "",
        "## Executed Cases",
        "",
    ]
    for case_id in report["executable_case_ids"]:
        lines.append(f"- `{case_id}`")
    if not report["executable_case_ids"]:
        lines.append("- None")

    lines.extend(["", "## Skipped/documented Cases", ""])
    for item in report["skipped_case_ids"]:
        lines.append(f"- `{item['case_id']}`: {item['reason']}")
    if not report["skipped_case_ids"]:
        lines.append("- None")

    lines.extend(["", "## Review-needed Cases", ""])
    for case_id in report["review_needed_case_ids"]:
        lines.append(f"- `{case_id}`")
    if not report["review_needed_case_ids"]:
        lines.append("- None")

    lines.extend(["", "## Failure-class Breakdown", ""])
    for key, value in report["failure_class_counts"].items():
        lines.append(f"- `{key}`: {value}")

    lines.extend(["", "## Evidence-level Breakdown", ""])
    for key, value in report["evidence_level_counts"].items():
        lines.append(f"- `{key}`: {value}")

    lines.extend(
        [
            "",
            "## Authority Boundary",
            "",
            report["authority_boundary"],
            "",
            report["safe_claim"],
            "",
            report["no_official_authority_statement"],
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the public Parva conformance suite.")
    parser.add_argument("--case-root", default=str(ROOT / "conformance"), help="Case root directory")
    parser.add_argument("--suite", default="default", choices=["default", "public-nepali-date-issues"])
    parser.add_argument("--profile", choices=["nepal-compliance"], help="Run a named conformance profile")
    parser.add_argument("--api", action="store_true", help="Also run supported cases against API")
    parser.add_argument(
        "--write-report",
        help="Write a public issue suite report. The Markdown report is written next to the JSON path.",
    )
    args = parser.parse_args(argv)

    api_base_url = None
    if args.api:
        api_base_url = os.environ.get("PARVA_CONFORMANCE_BASE_URL")
        if not api_base_url:
            print("--api requires PARVA_CONFORMANCE_BASE_URL", file=sys.stderr)
            return 2

    try:
        if args.profile:
            profile, summary = run_profile(args.profile, Path(args.case_root))
            print("Parva conformance profile summary")
            print(f"profile: {profile['id']}")
            print(f"description: {profile['description']}")
            print(f"case_root: {Path(args.case_root)}")
            print(f"total: {summary.total}")
            print(f"executed: {summary.executed}")
            print(f"passed: {summary.passed}")
            print(f"failed: {summary.failed}")
            print(f"skipped: {summary.skipped}")
            print(f"review_needed: {summary.review_needed}")
            for result in summary.results:
                status = "PASS" if result.passed else "FAIL"
                print(f"{status} {result.file} :: {result.case_id} :: {result.message}")
            if args.write_report:
                case_ids = {str(case_id) for case_id in profile["related_public_cases"]}
                report = _public_issue_report(
                    summary,
                    Path(args.case_root),
                    suite_name=f"profile:{profile['id']}",
                    case_ids=case_ids,
                )
                json_path, md_path = _write_public_issue_report(report, Path(args.write_report))
                print(f"wrote_report_json: {_display_path(json_path)}")
                print(f"wrote_report_md: {_display_path(md_path)}")
            return 1 if summary.failed else 0

        if args.suite == "public-nepali-date-issues":
            summary = run_public_issue_suite(Path(args.case_root))
            print("Parva public issue conformance summary")
            print(f"case_root: {Path(args.case_root)}")
            print(f"total: {summary.total}")
            print(f"executed: {summary.executed}")
            print(f"passed: {summary.passed}")
            print(f"failed: {summary.failed}")
            print(f"skipped: {summary.skipped}")
            print(f"review_needed: {summary.review_needed}")
            for result in summary.results:
                status = "PASS" if result.passed else "FAIL"
                print(f"{status} {result.file} :: {result.case_id} :: {result.message}")
            if args.write_report:
                report = _public_issue_report(
                    summary,
                    Path(args.case_root),
                    suite_name="public-nepali-date-issues",
                )
                json_path, md_path = _write_public_issue_report(report, Path(args.write_report))
                print(f"wrote_report_json: {_display_path(json_path)}")
                print(f"wrote_report_md: {_display_path(md_path)}")
            return 1 if summary.failed else 0

        if args.write_report:
            print("--write-report is supported for public issue suites and profiles only", file=sys.stderr)
            return 2

        failures, results = run(Path(args.case_root), api_base_url=api_base_url)
    except Exception as exc:  # noqa: BLE001
        print(f"Conformance setup failed: {exc}", file=sys.stderr)
        return 1

    passed = len(results) - failures
    print("Parva conformance summary")
    print(f"case_root: {Path(args.case_root)}")
    print(f"total: {len(results)}")
    print(f"passed: {passed}")
    print(f"failed: {failures}")
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"{status} {result.file} :: {result.case_id} :: {result.message}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
