#!/usr/bin/env python3
"""Smoke-check a deployed Project Parva base URL."""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Check:
    name: str
    method: str
    path: str
    expected_status: int = 200
    body: dict[str, Any] | None = None
    must_contain: tuple[str, ...] = ()


CHECKS = (
    Check("health", "GET", "/health"),
    Check("ready", "GET", "/health/ready"),
    Check("calendar_convert", "GET", "/v3/api/calendar/convert?date=2026-04-14"),
    Check("festivals_upcoming", "GET", "/v3/api/festivals/upcoming?days=30"),
    Check("trust_capabilities", "GET", "/v3/api/trust/capabilities"),
    Check("protocol_version", "GET", "/v3/api/protocol/version"),
    Check("route_profile_policy", "GET", "/v3/api/policy"),
    Check("openapi", "GET", "/openapi.json"),
    Check("private_future_prediction_blocked", "GET", "/v4/api/future-bs/month-lengths?start=2090&end=2091", expected_status=404),
)


def _request(base_url: str, check: Check, timeout: float) -> dict[str, Any]:
    url = urllib.parse.urljoin(base_url.rstrip("/") + "/", check.path.lstrip("/"))
    data = None
    headers = {"User-Agent": "parva-deployment-smoke/1"}
    if check.body is not None:
        data = json.dumps(check.body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=check.method)
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(1024 * 1024)
            status = int(response.status)
    except urllib.error.HTTPError as exc:
        body = exc.read(1024 * 1024)
        status = int(exc.code)
    elapsed_ms = round((time.perf_counter() - started) * 1000.0, 3)
    text = body.decode("utf-8", errors="replace")
    contains_ok = all(fragment in text for fragment in check.must_contain)
    return {
        "name": check.name,
        "method": check.method,
        "path": check.path,
        "status": status,
        "expected_status": check.expected_status,
        "latency_ms": elapsed_ms,
        "bytes": len(body),
        "ok": status == check.expected_status and contains_ok,
        "snippet": text[:300],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--timeout", type=float, default=8.0)
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    results = []
    failures = []
    for check in CHECKS:
        try:
            row = _request(args.base_url, check, args.timeout)
        except (OSError, urllib.error.URLError) as exc:
            row = {
                "name": check.name,
                "method": check.method,
                "path": check.path,
                "status": None,
                "expected_status": check.expected_status,
                "ok": False,
                "error": str(exc),
            }
        results.append(row)
        if not row["ok"]:
            failures.append(row)

    report = {
        "base_url": args.base_url,
        "generated_at_unix": int(time.time()),
        "summary": {"checks": len(results), "failures": len(failures)},
        "results": results,
    }
    if args.output:
        from pathlib import Path

        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report["summary"], sort_keys=True))
    if failures:
        for failure in failures:
            print(f"FAIL {failure['name']}: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
