#!/usr/bin/env python3
"""Measure route latency against the local app or a deployed base URL."""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@dataclass(frozen=True)
class Probe:
    path: str
    method: str = "GET"
    json_payload: dict[str, Any] | None = None
    lane: str = "stable_public"
    local_budget_ms: float = 300.0
    deployed_budget_ms: float = 500.0
    max_payload_bytes: int = 262144
    profiles: tuple[str, ...] = ("public_reference",)


PROBES: tuple[Probe, ...] = (
    Probe("/health", lane="stable_core", local_budget_ms=25, deployed_budget_ms=100, max_payload_bytes=8192),
    Probe("/health/ready", lane="stable_core", local_budget_ms=50, deployed_budget_ms=150),
    Probe(
        "/v3/api/calendar/convert?date=2026-04-14",
        lane="stable_core",
        local_budget_ms=75,
        deployed_budget_ms=200,
    ),
    Probe(
        "/v3/api/calendar/today",
        lane="stable_public",
        local_budget_ms=300,
        deployed_budget_ms=600,
        max_payload_bytes=65536,
    ),
    Probe(
        "/v3/api/festivals/upcoming?days=30&from_date=2026-10-21&quality_band=all",
        lane="stable_public",
        local_budget_ms=300,
        deployed_budget_ms=500,
        max_payload_bytes=262144,
    ),
    Probe(
        "/v3/api/protocol/version",
        lane="protocol_draft",
        local_budget_ms=100,
        deployed_budget_ms=250,
        max_payload_bytes=65536,
    ),
)


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * pct)))
    return ordered[index]


def _request_local(client: Any, probe: Probe) -> tuple[int, int]:
    if probe.method == "POST":
        response = client.post(probe.path, json=probe.json_payload or {})
    else:
        response = client.get(probe.path)
    return response.status_code, len(response.content)


def _request_remote(base_url: str, probe: Probe, timeout: float) -> tuple[int, int]:
    url = base_url.rstrip("/") + probe.path
    data = None
    headers = {}
    if probe.method == "POST":
        data = json.dumps(probe.json_payload or {}).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=probe.method)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read()
        return int(response.status), len(body)


def _measure_probe(
    probe: Probe,
    *,
    client: Any | None,
    base_url: str | None,
    warmup_requests: int,
    measured_requests: int,
    timeout: float,
) -> dict[str, Any]:
    latencies: list[float] = []
    statuses: list[int] = []
    payload_sizes: list[int] = []
    errors: list[str] = []

    def call_once() -> None:
        started = time.perf_counter()
        try:
            if client is not None:
                status_code, size = _request_local(client, probe)
            elif base_url is not None:
                status_code, size = _request_remote(base_url, probe, timeout)
            else:
                raise RuntimeError("no client or base URL configured")
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            statuses.append(status_code)
            payload_sizes.append(size)
            latencies.append(elapsed_ms)
        except (OSError, urllib.error.URLError, RuntimeError) as exc:
            errors.append(str(exc))

    for _ in range(warmup_requests):
        call_once()
    latencies.clear()
    statuses.clear()
    payload_sizes.clear()
    errors.clear()

    for _ in range(measured_requests):
        call_once()

    p50 = statistics.median(latencies) if latencies else None
    p95 = _percentile(latencies, 0.95) if latencies else None
    max_latency = max(latencies) if latencies else None
    max_payload = max(payload_sizes) if payload_sizes else 0
    return {
        "path": probe.path,
        "method": probe.method,
        "lane": probe.lane,
        "requests": measured_requests,
        "statuses": statuses,
        "payload_bytes_max": max_payload,
        "budget_ms": probe.deployed_budget_ms if base_url else probe.local_budget_ms,
        "max_payload_bytes": probe.max_payload_bytes,
        "p50_ms": round(p50, 3) if p50 is not None else None,
        "p95_ms": round(p95, 3) if p95 is not None else None,
        "max_ms": round(max_latency, 3) if max_latency is not None else None,
        "errors": errors,
    }


def _load_local_app(route_profile: str):
    os.environ.setdefault("PARVA_ENV", "test")
    os.environ.setdefault("PARVA_RATE_LIMIT_ENABLED", "false")
    os.environ.setdefault("PARVA_PLACE_SEARCH_ALLOW_REMOTE", "false")
    os.environ["PARVA_ROUTE_PROFILE"] = route_profile
    from app.bootstrap.app_factory import create_app
    from fastapi.testclient import TestClient

    return TestClient(create_app())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="public_reference")
    parser.add_argument("--base-url", default="")
    parser.add_argument("--output", required=True)
    parser.add_argument("--warmup-requests", type=int, default=2)
    parser.add_argument("--requests", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()

    selected = [probe for probe in PROBES if args.profile in probe.profiles]
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    client = None if args.base_url else _load_local_app(args.profile)
    if client is not None:
        context = client
    else:
        context = None

    results: list[dict[str, Any]] = []
    if context is None:
        for probe in selected:
            results.append(
                _measure_probe(
                    probe,
                    client=None,
                    base_url=args.base_url,
                    warmup_requests=args.warmup_requests,
                    measured_requests=args.requests,
                    timeout=args.timeout,
                )
            )
    else:
        with context as active_client:
            for probe in selected:
                results.append(
                    _measure_probe(
                        probe,
                        client=active_client,
                        base_url=None,
                        warmup_requests=args.warmup_requests,
                        measured_requests=args.requests,
                        timeout=args.timeout,
                    )
                )

    failures: list[str] = []
    warnings: list[str] = []
    fail_lanes = {"stable_core", "stable_public"}
    for row in results:
        status_ok = row["statuses"] and all(status == 200 for status in row["statuses"])
        payload_ok = row["payload_bytes_max"] <= row["max_payload_bytes"]
        latency_ok = row["p95_ms"] is not None and row["p95_ms"] <= row["budget_ms"]
        issue = None
        if row["errors"]:
            issue = f"{row['method']} {row['path']} errors: {row['errors'][:2]}"
        elif not status_ok:
            issue = f"{row['method']} {row['path']} statuses={row['statuses']}"
        elif not payload_ok:
            issue = (
                f"{row['method']} {row['path']} payload {row['payload_bytes_max']} "
                f"> {row['max_payload_bytes']}"
            )
        elif not latency_ok:
            issue = f"{row['method']} {row['path']} p95 {row['p95_ms']} > {row['budget_ms']}"
        if issue and row["lane"] in fail_lanes:
            failures.append(issue)
        elif issue:
            warnings.append(issue)

    report = {
        "profile": args.profile,
        "mode": "deployed" if args.base_url else "local_in_process",
        "base_url": args.base_url or None,
        "generated_at_unix": int(time.time()),
        "summary": {
            "route_count": len(results),
            "failures": len(failures),
            "warnings": len(warnings),
        },
        "results": results,
        "failures": failures,
        "warnings": warnings,
    }
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote latency report to {output_path}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    for warning in warnings:
        print(f"WARN: {warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
