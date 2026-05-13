"""Measure public API endpoint latency with the local FastAPI app."""

from __future__ import annotations

import json
import logging
import statistics
import time
from dataclasses import dataclass
from typing import Any

from app.main import app
from fastapi.testclient import TestClient


@dataclass(frozen=True)
class EndpointProbe:
    name: str
    method: str
    path: str
    kwargs: dict[str, Any]
    budget_ms: float


PROBES = [
    EndpointProbe("health", "GET", "/health", {}, 50.0),
    EndpointProbe("ready", "GET", "/health/ready", {}, 100.0),
    EndpointProbe("today", "GET", "/v3/api/calendar/today", {}, 100.0),
    EndpointProbe(
        "ad_to_bs",
        "GET",
        "/v3/api/calendar/convert",
        {"params": {"date": "2026-04-14"}},
        100.0,
    ),
    EndpointProbe(
        "bs_to_ad",
        "POST",
        "/v3/api/calendar/bs-to-gregorian",
        {"json": {"year": 2083, "month": 1, "day": 1}},
        100.0,
    ),
    EndpointProbe(
        "month_calendar",
        "GET",
        "/v3/api/calendar/dual-month",
        {"params": {"year": 2026, "month": 4}},
        200.0,
    ),
    EndpointProbe("fiscal_year", "GET", "/v3/api/enterprise/fiscal-year/2082", {}, 100.0),
    EndpointProbe("bs_months", "GET", "/v3/api/enterprise/bs-months/2082", {}, 100.0),
    EndpointProbe(
        "business_days",
        "POST",
        "/v3/api/enterprise/business-days",
        {"json": {"start_bs": "2082-01-01", "end_bs": "2082-01-07"}},
        200.0,
    ),
    EndpointProbe(
        "upcoming_festivals",
        "GET",
        "/v3/api/festivals/upcoming",
        {"params": {"days": 30, "quality_band": "computed"}},
        500.0,
    ),
]


def _request(client: TestClient, probe: EndpointProbe):
    if probe.method == "GET":
        return client.get(probe.path, **probe.kwargs)
    if probe.method == "POST":
        return client.post(probe.path, **probe.kwargs)
    raise ValueError(f"Unsupported probe method: {probe.method}")


def measure(rounds: int = 3) -> dict[str, Any]:
    client = TestClient(app)
    results = []
    for probe in PROBES:
        # Warm the route once so this script reports hot endpoint behavior.
        _request(client, probe)
        durations = []
        statuses = []
        for _ in range(rounds):
            started = time.perf_counter()
            response = _request(client, probe)
            durations.append((time.perf_counter() - started) * 1000.0)
            statuses.append(response.status_code)
        p50 = statistics.median(durations)
        max_ms = max(durations)
        results.append(
            {
                "name": probe.name,
                "method": probe.method,
                "path": probe.path,
                "status_codes": statuses,
                "p50_ms": round(p50, 2),
                "max_ms": round(max_ms, 2),
                "budget_ms": probe.budget_ms,
                "within_budget": max_ms <= probe.budget_ms,
            }
        )
    return {
        "rounds": rounds,
        "publication_status": "computed_prediction_not_official",
        "results": results,
    }


def main() -> int:
    logging.getLogger().setLevel(logging.CRITICAL)
    print(json.dumps(measure(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
