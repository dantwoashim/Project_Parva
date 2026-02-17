"""
Benchmark Runner
=================

CLI tool that runs any calendar engine against the Parva Benchmark
and produces a standardized score.

Usage:
    python -m backend.tools.benchmark_runner --year 2025 --format markdown
"""

import json
import sys
import time
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.calendar.calculator_v2 import calculate_festival_v2, list_festivals_v2
from app.calendar.bikram_sambat import gregorian_to_bs, bs_to_gregorian
from app.calendar.tithi.tithi_udaya import get_udaya_tithi
from app.calendar.panchanga import get_panchanga


# ── Benchmark Test Suites ─────────────────────────────────────────

def bench_bs_round_trip(years: int = 100) -> Dict:
    """Benchmark: BS ↔ Gregorian round-trip accuracy."""
    start = time.time()
    passed = 0
    failed = 0

    for year in range(2020, 2020 + years):
        for month in range(1, 13):
            for day in [1, 15]:
                try:
                    d = date(year, month, day)
                    bs_y, bs_m, bs_d = gregorian_to_bs(d)
                    greg_back = bs_to_gregorian(bs_y, bs_m, bs_d)
                    if greg_back == d:
                        passed += 1
                    else:
                        failed += 1
                except Exception:
                    failed += 1

    elapsed = time.time() - start
    total = passed + failed
    return {
        "suite": "bs_round_trip",
        "total": total,
        "passed": passed,
        "failed": failed,
        "accuracy": passed / total if total > 0 else 0,
        "elapsed_seconds": round(elapsed, 3),
    }


def bench_tithi_consistency(days: int = 365) -> Dict:
    """Benchmark: tithi computation consistency over N days."""
    start = time.time()
    passed = 0
    failed = 0
    base = date(2025, 1, 1)

    for i in range(days):
        try:
            d = date.fromordinal(base.toordinal() + i)
            result = get_udaya_tithi(d)
            if (
                1 <= result["tithi"] <= 15
                and result["paksha"] in ("shukla", "krishna")
                and 0 <= result["progress"] <= 1
            ):
                passed += 1
            else:
                failed += 1
        except Exception:
            failed += 1

    elapsed = time.time() - start
    total = passed + failed
    return {
        "suite": "tithi_consistency",
        "total": total,
        "passed": passed,
        "failed": failed,
        "accuracy": passed / total if total > 0 else 0,
        "elapsed_seconds": round(elapsed, 3),
    }


def bench_festival_calculation(year: int = 2025) -> Dict:
    """Benchmark: festival date calculation success rate."""
    start = time.time()
    all_festivals = list_festivals_v2()
    passed = 0
    failed = 0
    errors = []

    for fid in all_festivals:
        try:
            result = calculate_festival_v2(fid, year)
            if result and result.start_date:
                passed += 1
            else:
                failed += 1
                errors.append({"festival_id": fid, "error": "returned None"})
        except Exception as e:
            failed += 1
            errors.append({"festival_id": fid, "error": str(e)})

    elapsed = time.time() - start
    total = passed + failed
    return {
        "suite": "festival_calculation",
        "year": year,
        "total": total,
        "passed": passed,
        "failed": failed,
        "accuracy": passed / total if total > 0 else 0,
        "elapsed_seconds": round(elapsed, 3),
        "errors": errors[:5],  # First 5 errors
    }


def run_full_benchmark(year: int = 2025) -> Dict:
    """Run all benchmark suites and produce aggregate score."""
    suites = [
        bench_bs_round_trip(years=10),
        bench_tithi_consistency(days=30),
        bench_festival_calculation(year),
    ]

    total_passed = sum(s["passed"] for s in suites)
    total_tests = sum(s["total"] for s in suites)
    total_time = sum(s["elapsed_seconds"] for s in suites)

    return {
        "benchmark": "Parva Benchmark v1.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "year": year,
        "suites": suites,
        "aggregate": {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "overall_accuracy": total_passed / total_tests if total_tests > 0 else 0,
            "total_time_seconds": round(total_time, 3),
        },
    }


def format_markdown(results: Dict) -> str:
    """Format benchmark results as Markdown."""
    lines = [
        f"# Parva Benchmark Report",
        f"",
        f"**Date**: {results['timestamp']}",
        f"**Year**: {results['year']}",
        f"",
        f"## Aggregate",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total Tests | {results['aggregate']['total_tests']} |",
        f"| Passed | {results['aggregate']['total_passed']} |",
        f"| Accuracy | {results['aggregate']['overall_accuracy']*100:.1f}% |",
        f"| Time | {results['aggregate']['total_time_seconds']}s |",
        f"",
        f"## Suites",
        f"",
    ]

    for s in results["suites"]:
        lines.append(f"### {s['suite']}")
        lines.append(f"- Passed: {s['passed']}/{s['total']} ({s['accuracy']*100:.1f}%)")
        lines.append(f"- Time: {s['elapsed_seconds']}s")
        lines.append("")

    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Parva Benchmark Runner")
    parser.add_argument("--year", type=int, default=2025)
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    results = run_full_benchmark(args.year)

    if args.format == "markdown":
        output = format_markdown(results)
    else:
        output = json.dumps(results, indent=2)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
