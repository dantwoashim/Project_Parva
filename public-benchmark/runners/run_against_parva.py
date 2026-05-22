#!/usr/bin/env python3
"""Run the public Nepali Time Reliability Benchmark against a Parva deployment."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
PROJECT_ROOT = ROOT.parent
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from validate_benchmark import validate_benchmark_document  # noqa: E402

WEIGHTS = {
    "correctness": 40,
    "source_awareness": 20,
    "uncertainty_handling": 20,
    "review_gate_behavior": 10,
    "machine_readable_structure": 10,
}


@dataclass(frozen=True)
class RequestSpec:
    method: str
    path: str
    params: dict[str, str] | None = None
    body: dict[str, Any] | None = None


FetchResult = tuple[int, Any]
Fetcher = Callable[[str, RequestSpec, float], FetchResult]
_INPROCESS_CLIENT: Any | None = None
RESULTS_PATH = ROOT / "results" / "latest-parva.json"


def _load_benchmark() -> dict[str, Any]:
    benchmark = json.loads((ROOT / "benchmark.json").read_text(encoding="utf-8"))
    issues = validate_benchmark_document(benchmark)
    if issues:
        raise ValueError("; ".join(issues))
    return benchmark


def _parse_bs_date(value: str) -> tuple[int, int, int]:
    year, month, day = value.split("-", 2)
    return int(year), int(month), int(day)


def _url(base_url: str, spec: RequestSpec) -> str:
    base = base_url.rstrip("/")
    query = urllib.parse.urlencode(spec.params or {})
    return f"{base}{spec.path}{'?' + query if query else ''}"


def fetch_json(base_url: str, spec: RequestSpec, timeout: float) -> FetchResult:
    if base_url.startswith("inprocess://"):
        return _fetch_inprocess(spec)

    data = None
    headers = {"Accept": "application/json"}
    if spec.body is not None:
        data = json.dumps(spec.body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(_url(base_url, spec), data=data, headers=headers, method=spec.method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            payload: Any = json.loads(body)
        except json.JSONDecodeError:
            payload = {"error": body}
        return exc.code, payload


def _fetch_inprocess(spec: RequestSpec) -> FetchResult:
    global _INPROCESS_CLIENT
    if _INPROCESS_CLIENT is None:
        os.environ.setdefault("PARVA_ENV", "test")
        os.environ.setdefault("PARVA_ROUTE_PROFILE", "public_reference")
        os.environ.setdefault("PARVA_ENABLE_EXPERIMENTAL_API", "false")
        os.environ.setdefault("PARVA_ENABLE_RESEARCH_API", "false")
        os.environ.setdefault("PARVA_SHOW_PRIVATE_SCHEMA", "false")
        os.environ.setdefault("PARVA_RATE_LIMIT_ENABLED", "false")
        os.environ.setdefault("PARVA_REQUIRE_PRECOMPUTED", "false")
        from app.bootstrap.app_factory import create_app
        from fastapi.testclient import TestClient

        _INPROCESS_CLIENT = TestClient(create_app())

    response = _INPROCESS_CLIENT.request(
        spec.method,
        spec.path,
        params=spec.params,
        json=spec.body,
    )
    try:
        payload: Any = response.json()
    except ValueError:
        payload = {"error": response.text}
    return response.status_code, payload


def _request_for_task(task: dict[str, Any]) -> RequestSpec:
    category = task["category"]
    item = task.get("input", {})

    if category == "bs_ad_conversion":
        if "ad_date" in item:
            return RequestSpec("GET", "/v3/api/calendar/convert", params={"date": item["ad_date"]})
        year, month, day = _parse_bs_date(item["bs_date"])
        return RequestSpec(
            "POST",
            "/v3/api/calendar/bs-to-gregorian",
            body={"year": year, "month": month, "day": day},
        )
    if category == "ad_bs_conversion":
        return RequestSpec("GET", "/v3/api/calendar/convert", params={"date": item["ad_date"]})
    if category in {"valid_invalid_bs_dates", "invalid_bs_dates"}:
        year, month, day = _parse_bs_date(item["bs_date"])
        return RequestSpec("POST", "/v3/api/calendar/bs-to-gregorian", body={"year": year, "month": month, "day": day})
    if category == "fiscal_year_boundaries":
        bs_year = int(item.get("bs_year") or str(item.get("bs_date", "2082")).split("-", 1)[0])
        return RequestSpec("GET", f"/v3/api/enterprise/fiscal-year/{bs_year}")
    if category in {"working_day_shifts", "repayment_payroll_due_date_logic", "working_days", "payroll_repayment_review_gates"}:
        bs_date = item.get("bs_date") or item.get("start_bs", "2082-04-02")
        if category in {"working_days"} and "start_bs" in item and "end_bs" in item:
            return RequestSpec(
                "POST",
                "/v3/api/enterprise/business-days",
                body={"start_bs": item["start_bs"], "end_bs": item["end_bs"], "holiday_policy": item.get("holiday_policy", "none")},
            )
        return RequestSpec(
            "POST",
            "/v3/api/compliance/evaluate-date",
            body={
                "profile_id": item.get("profile_id", "nepal_private_company_default"),
                "bs_date": bs_date,
                "decision_intent": item.get("workflow_type", "general"),
            },
        )
    if category in {"public_holidays", "holidays"}:
        if item.get("route"):
            raw_route = str(item["route"])
            path, _, query = raw_route.partition("?")
            params = dict(urllib.parse.parse_qsl(query)) if query else None
            return RequestSpec("GET", path, params=params)
        if "bs_date" in item or "ad_date" in item:
            return RequestSpec(
                "POST",
                "/v3/api/compliance/evaluate-date",
                body={
                    "profile_id": item.get("profile_id", "nepal_private_company_default"),
                    "bs_date": item.get("bs_date"),
                    "ad_date": item.get("ad_date"),
                    "decision_intent": "general",
                },
            )
        return RequestSpec("GET", "/v3/api/festivals/upcoming", params={"days": "30"})
    if category == "festival_dates":
        festival = item.get("festival", "dashain")
        year = str(item.get("year", 2026))
        return RequestSpec("GET", f"/v3/api/festivals/{festival}", params={"year": year})
    if category in {"panchanga_tithi", "panchanga_tithi_at_sunrise"}:
        return RequestSpec("GET", "/v3/api/calendar/panchanga", params={"date": item.get("ad_date", "2026-04-14")})
    if category in {"future_bs_review_required", "future_bs_unsupported_review_required"}:
        return RequestSpec("GET", "/v4/api/future-bs/capabilities")
    if category in {"source_confidence_review_metadata", "source_confidence_evidence_metadata"}:
        return RequestSpec("GET", str(item.get("route", "/v3/api/policy")))
    if category == "static_naive_baseline":
        return RequestSpec("GET", "/v3/api/policy")
    raise ValueError(f"Unsupported benchmark category: {category}")


def _walk(value: Any):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _contains_key(payload: Any, keys: set[str]) -> bool:
    return any(isinstance(item, dict) and any(key in item for key in keys) for item in _walk(payload))


def _contains_pair(payload: Any, key: str, expected: Any) -> bool:
    return any(isinstance(item, dict) and item.get(key) == expected for item in _walk(payload))


def _get_path(payload: Any, dotted: str) -> Any:
    cursor = payload
    for part in dotted.split("."):
        if not isinstance(cursor, dict) or part not in cursor:
            return None
        cursor = cursor[part]
    return cursor


def _correctness(task: dict[str, Any], status: int, payload: Any) -> bool:
    expected = task.get("expected", {})
    category = task["category"]
    if category == "bs_ad_conversion":
        if "ad_date" in expected:
            return status == 200 and (payload.get("gregorian") or payload.get("ad_date")) == expected.get("ad_date")
        if {"bs_year", "bs_month", "bs_day"} & set(expected):
            bs = payload.get("bikram_sambat", {}) if isinstance(payload, dict) else {}
            return status == 200 and all(
                bs.get(key) == expected.get(f"bs_{key}")
                for key in ("year", "month", "day")
                if f"bs_{key}" in expected
            )
        return status == 200
    if category == "ad_bs_conversion":
        if not {"bs_year", "bs_month", "bs_day"} & set(expected):
            return status == 200
        bs = payload.get("bikram_sambat", {}) if isinstance(payload, dict) else {}
        return status == 200 and all(
            bs.get(key) == expected.get(f"bs_{key}")
            for key in ("year", "month", "day")
            if f"bs_{key}" in expected
        )
    if category in {"valid_invalid_bs_dates", "invalid_bs_dates"}:
        if "valid" not in expected:
            return status == 200
        wants_valid = bool(expected.get("valid"))
        return status < 400 if wants_valid else status >= 400
    if category == "fiscal_year_boundaries":
        if "fiscal_year" not in expected:
            return status == 200
        return status == 200 and payload.get("fiscal_year") == expected.get("fiscal_year")
    if category in {"future_bs_review_required", "future_bs_unsupported_review_required"}:
        publication_status = expected.get("publication_status")
        return status == 200 and (
            not publication_status or _contains_pair(payload, "publication_status", publication_status)
        )
    return status == 200


def _evaluate_task(task: dict[str, Any], status: int, payload: Any) -> dict[str, Any]:
    expected = task.get("expected", {})
    signals = {
        "correctness": _correctness(task, status, payload),
        "source_awareness": _contains_key(payload, {"source", "sources", "source_metadata", "provenance", "policy", "meta"}),
        "uncertainty_handling": _contains_key(payload, {"confidence", "uncertainty", "risk", "publication_status", "claim_boundary", "review_required"}),
        "review_gate_behavior": status in {400, 403} or _contains_key(
            payload,
            {
                "review_required",
                "human_review_required",
                "requires_human_review",
                "unsupported",
                "not_legal_authority",
            },
        ),
        "machine_readable_structure": isinstance(payload, (dict, list)),
    }

    if expected.get("source_metadata_required"):
        signals["source_awareness"] = signals["source_awareness"] or _contains_key(payload, {"sources", "source_id"})
    if expected.get("method_metadata_required"):
        signals["uncertainty_handling"] = signals["uncertainty_handling"] or _contains_key(payload, {"method", "engine_version", "ephemeris"})
    if expected.get("review_required"):
        signals["review_gate_behavior"] = (
            signals["review_gate_behavior"]
            or _contains_pair(payload, "review_required", True)
            or _contains_pair(payload, "requires_human_review", True)
            or _contains_pair(payload, "human_review_required", True)
        )
    if expected.get("not_legal_authority"):
        signals["review_gate_behavior"] = signals["review_gate_behavior"] or _contains_key(payload, {"policy", "claim_boundary"})
    if expected.get("exact_predictions_public") is False:
        serialized = json.dumps(payload, ensure_ascii=False).lower()
        signals["review_gate_behavior"] = "computed_prediction_not_official" in serialized and "exact_predictions" not in serialized
    if expected.get("machine_readable"):
        signals["machine_readable_structure"] = isinstance(payload, (dict, list))

    score = sum(weight for key, weight in WEIGHTS.items() if signals[key])
    return {
        "id": task["id"],
        "category": task["category"],
        "http_status": status,
        "status": "pass" if signals["correctness"] else "fail",
        "signals": signals,
        "score": score,
    }


def run_benchmark(base_url: str, *, timeout: float = 20.0, fetcher: Fetcher = fetch_json) -> dict[str, Any]:
    benchmark = _load_benchmark()
    results = []
    for task in benchmark["tasks"]:
        try:
            spec = _request_for_task(task)
            status, payload = fetcher(base_url, spec, timeout)
            result = _evaluate_task(task, status, payload)
        except Exception as exc:  # noqa: BLE001 - benchmark output should record every task.
            result = {
                "id": task["id"],
                "category": task["category"],
                "http_status": None,
                "status": "blocked",
                "error": str(exc),
                "signals": {key: False for key in WEIGHTS},
                "score": 0,
            }
        results.append(result)

    total = len(results)
    score = sum(item["score"] for item in results)
    max_score = total * sum(WEIGHTS.values())
    return {
        "runner": "parva",
        "base_url": base_url.rstrip("/"),
        "schema_version": benchmark["schema_version"],
        "summary": {
            "total": total,
            "passed": sum(1 for item in results if item["status"] == "pass"),
            "failed": sum(1 for item in results if item["status"] == "fail"),
            "blocked": sum(1 for item in results if item["status"] == "blocked"),
            "score": score,
            "max_score": max_score,
            "score_percent": round((score / max_score) * 100.0, 2) if max_score else 0.0,
        },
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="inprocess://parva")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--fail-under", type=float, default=None, help="Exit nonzero if score_percent is below this value.")
    args = parser.parse_args(argv)

    report = run_benchmark(args.base_url, timeout=args.timeout)
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.fail_under is not None and report["summary"]["score_percent"] < args.fail_under:
        return 1
    return 0 if report["summary"]["blocked"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
