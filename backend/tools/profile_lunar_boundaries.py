#!/usr/bin/env python3
"""Profile lunar month boundary computation speed."""

from __future__ import annotations

from pathlib import Path
from statistics import mean, median
from time import perf_counter
import os

from app.calendar.lunar_calendar import lunar_month_boundaries


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    idx = int((len(values) - 1) * p)
    return sorted(values)[idx]


def main() -> None:
    years = list(range(2020, 2031))
    durations_ms: list[float] = []
    rows: list[tuple[int, int, float]] = []

    for year in years:
        t0 = perf_counter()
        boundaries = lunar_month_boundaries(year)
        elapsed_ms = (perf_counter() - t0) * 1000.0
        durations_ms.append(elapsed_ms)
        rows.append((year, len(boundaries), elapsed_ms))

    out_dir = Path(os.environ.get("OUTPUT_DIR", Path(__file__).resolve().parents[2] / "docs" / "weekly_execution" / "year1_week20"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "lunar_boundary_performance.md"

    lines = [
        "# Lunar Boundary Performance (Week 20)",
        "",
        f"Run years: {years[0]}-{years[-1]} ({len(years)} samples)",
        "",
        f"- Average: {mean(durations_ms):.3f} ms",
        f"- Median: {median(durations_ms):.3f} ms",
        f"- P95: {percentile(durations_ms, 0.95):.3f} ms",
        f"- Max: {max(durations_ms):.3f} ms",
        "",
        "## Per-Year",
        "",
        "| Year | Boundaries | Time (ms) |",
        "|---|---:|---:|",
    ]

    for year, count, elapsed in rows:
        lines.append(f"| {year} | {count} | {elapsed:.3f} |")

    out_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()
