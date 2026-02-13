"""Profile tithi calculation latency."""

from __future__ import annotations

import statistics
import time
from datetime import date, timedelta
from pathlib import Path

from app.calendar.tithi.tithi_udaya import get_udaya_tithi


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    k = (len(values) - 1) * p
    f = int(k)
    c = min(f + 1, len(values) - 1)
    if f == c:
        return values[int(k)]
    return values[f] + (values[c] - values[f]) * (k - f)


def main() -> None:
    start = date(2026, 1, 1)
    times = []
    for i in range(200):
        d = start + timedelta(days=i)
        t0 = time.perf_counter()
        get_udaya_tithi(d)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)

    p95 = percentile(times, 0.95)
    p99 = percentile(times, 0.99)

    text = f"""# Tithi Performance Profile (Week 16)

Run size: 200 calls to `get_udaya_tithi(date)`

- Average: {statistics.mean(times):.3f} ms
- Median: {statistics.median(times):.3f} ms
- P95: {p95:.3f} ms
- P99: {p99:.3f} ms
- Max: {max(times):.3f} ms

Threshold check: target is `< 50 ms` per call.
"""

    out = Path(__file__).resolve().parents[2] / "docs" / "weekly_execution" / "year1_week16" / "tithi_performance.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
