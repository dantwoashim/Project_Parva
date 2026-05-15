#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date
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
]

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


def _load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ConformanceError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ConformanceError(f"{path}: root must be an object")
    return payload


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

    raise ConformanceError(f"{case['case_id']}: unsupported operation {operation!r}")


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the public Parva conformance suite.")
    parser.add_argument("--case-root", default=str(ROOT / "conformance"), help="Case root directory")
    parser.add_argument("--api", action="store_true", help="Also run supported cases against API")
    args = parser.parse_args(argv)

    api_base_url = None
    if args.api:
        api_base_url = os.environ.get("PARVA_CONFORMANCE_BASE_URL")
        if not api_base_url:
            print("--api requires PARVA_CONFORMANCE_BASE_URL", file=sys.stderr)
            return 2

    try:
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
