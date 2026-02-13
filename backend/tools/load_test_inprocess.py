#!/usr/bin/env python3
"""In-process load test for v2 panchanga endpoint."""

from __future__ import annotations

import asyncio
import statistics
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import httpx

from app.main import app

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_MD = PROJECT_ROOT / "docs" / "weekly_execution" / "year1_week36" / "load_test.md"


async def run_once(client: httpx.AsyncClient, path: str) -> tuple[int, float]:
    start = perf_counter()
    resp = await client.get(path)
    elapsed = (perf_counter() - start) * 1000.0
    return resp.status_code, elapsed


async def main_async(concurrency: int = 100) -> dict:
    path = "/v2/api/calendar/panchanga?date=2026-02-15"
    latencies = []
    statuses = []

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        tasks = [run_once(client, path) for _ in range(concurrency)]
        results = await asyncio.gather(*tasks)

    for status, latency in results:
        statuses.append(status)
        latencies.append(latency)

    success = sum(1 for s in statuses if s == 200)
    sorted_lat = sorted(latencies)

    def pct(p: float) -> float:
        if not sorted_lat:
            return 0.0
        idx = int((len(sorted_lat) - 1) * p)
        return sorted_lat[idx]

    return {
        "concurrency": concurrency,
        "success": success,
        "total": len(statuses),
        "error_rate": round((len(statuses) - success) / len(statuses) * 100.0, 2),
        "mean_ms": round(statistics.mean(latencies), 3),
        "p90_ms": round(pct(0.9), 3),
        "p95_ms": round(pct(0.95), 3),
        "p99_ms": round(pct(0.99), 3),
        "max_ms": round(max(latencies), 3),
    }


def write_report(stats: dict) -> None:
    lines = [
        "# In-Process Load Test (Week 36)",
        "",
        f"- Generated: `{datetime.now(timezone.utc).isoformat()}`",
        f"- Endpoint: `/v2/api/calendar/panchanga?date=2026-02-15`",
        f"- Concurrency: **{stats['concurrency']}**",
        f"- Success: **{stats['success']}/{stats['total']}**",
        f"- Error rate: **{stats['error_rate']}%**",
        "",
        "## Latency (ms)",
        "",
        f"- Mean: {stats['mean_ms']}",
        f"- P90: {stats['p90_ms']}",
        f"- P95: {stats['p95_ms']}",
        f"- P99: {stats['p99_ms']}",
        f"- Max: {stats['max_ms']}",
        "",
    ]

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    stats = asyncio.run(main_async())
    write_report(stats)
    print(stats)
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
