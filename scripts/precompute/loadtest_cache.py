#!/usr/bin/env python3
"""Simple in-process load test for cached panchanga endpoints."""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta, datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    rank = int(round((pct / 100) * (len(values) - 1)))
    return values[max(0, min(rank, len(values) - 1))]


def _build_dates(start: date, days: int) -> list[str]:
    return [(start + timedelta(days=i)).isoformat() for i in range(days)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Load test panchanga endpoint cache behavior")
    parser.add_argument("--requests", type=int, default=1000)
    parser.add_argument("--concurrency", type=int, default=25)
    parser.add_argument("--start-date", default=date.today().isoformat())
    parser.add_argument("--days", type=int, default=60)
    parser.add_argument("--out", default="reports/loadtest_m29.json")
    args = parser.parse_args()

    start = date.fromisoformat(args.start_date)
    pool = _build_dates(start, args.days)

    latencies: list[float] = []
    cache_hits = 0
    errors = 0
    t0 = time.perf_counter()

    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = []
        for _ in range(args.requests):
            d = random.choice(pool)
            futures.append(executor.submit(_request_one, d))

        for fut in as_completed(futures):
            ok, elapsed_ms, hit = fut.result()
            latencies.append(elapsed_ms)
            if not ok:
                errors += 1
            if hit:
                cache_hits += 1

    total_secs = time.perf_counter() - t0
    p95 = _percentile(latencies, 95)
    p99 = _percentile(latencies, 99)
    rps = args.requests / total_secs if total_secs else 0.0

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "requests": args.requests,
        "concurrency": args.concurrency,
        "date_pool": {"start": start.isoformat(), "days": args.days},
        "errors": errors,
        "cache_hits": cache_hits,
        "cache_hit_ratio": round(cache_hits / args.requests, 4) if args.requests else 0.0,
        "latency_ms": {
            "avg": round(statistics.mean(latencies), 2) if latencies else 0.0,
            "p95": round(p95, 2),
            "p99": round(p99, 2),
            "max": round(max(latencies), 2) if latencies else 0.0,
        },
        "throughput_rps": round(rps, 2),
        "simulated_req_per_min": int(rps * 60),
        "targets": {
            "cache_hit_ratio_panchanga": 0.90,
            "p95_ms": 500,
        },
        "target_status": {
            "cache_hit_ratio_panchanga": (cache_hits / args.requests) >= 0.90 if args.requests else False,
            "p95_ms": p95 <= 500,
        },
    }

    out = PROJECT_ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Wrote {out}")
    return 0


def _request_one(day: str) -> tuple[bool, float, bool]:
    client = TestClient(app)
    start = time.perf_counter()
    response = client.get("/api/calendar/panchanga", params={"date": day})
    elapsed_ms = (time.perf_counter() - start) * 1000
    ok = response.status_code == 200
    hit = False
    if ok:
        body = response.json()
        hit = bool(body.get("cache", {}).get("hit"))
    return ok, elapsed_ms, hit


if __name__ == "__main__":
    raise SystemExit(main())
