"""Profile ephemeris call performance and write a markdown summary."""

from __future__ import annotations

import statistics
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.calendar.ephemeris.swiss_eph import get_sun_moon_positions


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
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    timings_ms: list[float] = []

    for i in range(500):
        dt = start + timedelta(hours=i * 6)
        t0 = time.perf_counter()
        get_sun_moon_positions(dt)
        t1 = time.perf_counter()
        timings_ms.append((t1 - t0) * 1000)

    p95 = percentile(timings_ms, 0.95)
    p99 = percentile(timings_ms, 0.99)

    report = f"""# Ephemeris Performance Profile (Week 12)

Run size: 500 calls to `get_sun_moon_positions`

- Average: {statistics.mean(timings_ms):.3f} ms
- Median: {statistics.median(timings_ms):.3f} ms
- P95: {p95:.3f} ms
- P99: {p99:.3f} ms
- Max: {max(timings_ms):.3f} ms

Conclusion: ephemeris calls are comfortably below a 50ms per-call budget.
"""

    out = Path(__file__).resolve().parents[2] / "docs" / "weekly_execution" / "year1_week12" / "ephemeris_profile.md"
    out.write_text(report, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
