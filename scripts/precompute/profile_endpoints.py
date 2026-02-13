#!/usr/bin/env python3
"""Profile key endpoints for M29 hot-path and cold-path tracking."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402


def _probe(client: TestClient, endpoint: str, params: dict, iterations: int) -> dict:
    latencies = []
    failures = 0
    for _ in range(iterations):
        t0 = time.perf_counter()
        resp = client.get(endpoint, params=params)
        elapsed = (time.perf_counter() - t0) * 1000
        latencies.append(elapsed)
        if resp.status_code != 200:
            failures += 1
    latencies_sorted = sorted(latencies)
    p95_idx = int(0.95 * (len(latencies_sorted) - 1))
    p99_idx = int(0.99 * (len(latencies_sorted) - 1))
    return {
        "endpoint": endpoint,
        "params": params,
        "iterations": iterations,
        "failures": failures,
        "avg_ms": round(statistics.mean(latencies), 2) if latencies else 0.0,
        "p95_ms": round(latencies_sorted[p95_idx], 2) if latencies else 0.0,
        "p99_ms": round(latencies_sorted[p99_idx], 2) if latencies else 0.0,
        "max_ms": round(max(latencies), 2) if latencies else 0.0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Endpoint latency profiler")
    parser.add_argument("--iterations", type=int, default=50)
    parser.add_argument("--out", default="reports/m29_profile.json")
    args = parser.parse_args()

    today = date.today()
    samples = [
        ("/api/calendar/today", {}),
        ("/api/calendar/convert", {"date": today.isoformat()}),
        ("/api/calendar/panchanga", {"date": today.isoformat()}),
        ("/api/calendar/panchanga", {"date": (today + timedelta(days=180)).isoformat()}),
        ("/api/calendar/festivals/upcoming", {"days": 30}),
        ("/api/forecast/festivals", {"year": today.year + 20}),
    ]

    client = TestClient(app)
    rows = [_probe(client, endpoint, params, args.iterations) for endpoint, params in samples]
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "iterations_per_endpoint": args.iterations,
        "rows": rows,
    }

    out = PROJECT_ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
