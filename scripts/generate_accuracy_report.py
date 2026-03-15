"""
Annual Accuracy Benchmark Generator
====================================

Runs V2 calculator for known festivals against ground truth overrides.
Produces a structured accuracy report with mismatch taxonomy.
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OVERRIDES_PATH = PROJECT_ROOT / "backend" / "app" / "calendar" / "ground_truth_overrides.json"
REPORT_DIR = PROJECT_ROOT / "reports" / "accuracy"


def _load_overrides() -> dict[str, Any]:
    raw = json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def run_benchmark():
    """Compare V2 calculator output against ground truth for all years."""
    sys.path.insert(0, str(PROJECT_ROOT / "backend"))

    from app.calendar.calculator_v2 import calculate_festival_v2

    overrides = _load_overrides()
    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_years": sorted(overrides.keys()),
        "total_comparisons": 0,
        "exact_matches": 0,
        "off_by_one": 0,
        "off_by_more": 0,
        "calculator_failed": 0,
        "mismatches": [],
        "per_festival": {},
        "per_year": {},
    }

    for year_str, festivals in sorted(overrides.items()):
        year = int(year_str)
        year_stats = {"total": 0, "exact": 0, "off_1": 0, "off_more": 0, "failed": 0}

        for festival_id, truth in festivals.items():
            truth_date_str = truth.get("start")
            if not truth_date_str:
                continue

            results["total_comparisons"] += 1
            year_stats["total"] += 1

            try:
                truth_date = date.fromisoformat(truth_date_str)
            except ValueError:
                continue

            try:
                calc_result = calculate_festival_v2(festival_id, year)
            except Exception as exc:
                results["calculator_failed"] += 1
                year_stats["failed"] += 1
                results["mismatches"].append(
                    {
                        "festival_id": festival_id,
                        "year": year,
                        "truth": truth_date_str,
                        "computed": None,
                        "error": str(exc),
                        "category": "calculator_error",
                    }
                )
                continue

            if calc_result is None:
                results["calculator_failed"] += 1
                year_stats["failed"] += 1
                results["mismatches"].append(
                    {
                        "festival_id": festival_id,
                        "year": year,
                        "truth": truth_date_str,
                        "computed": None,
                        "error": "calculate_festival_v2 returned None",
                        "category": "not_in_catalog",
                    }
                )
                continue

            computed_date = calc_result.start_date
            delta_days = abs((computed_date - truth_date).days)

            if delta_days == 0:
                results["exact_matches"] += 1
                year_stats["exact"] += 1
            elif delta_days == 1:
                results["off_by_one"] += 1
                year_stats["off_1"] += 1
                results["mismatches"].append(
                    {
                        "festival_id": festival_id,
                        "year": year,
                        "truth": truth_date_str,
                        "computed": computed_date.isoformat(),
                        "delta_days": delta_days,
                        "method": calc_result.method,
                        "category": "off_by_one",
                    }
                )
            else:
                results["off_by_more"] += 1
                year_stats["off_more"] += 1
                results["mismatches"].append(
                    {
                        "festival_id": festival_id,
                        "year": year,
                        "truth": truth_date_str,
                        "computed": computed_date.isoformat(),
                        "delta_days": delta_days,
                        "method": calc_result.method,
                        "category": "significant_mismatch",
                    }
                )

            festival_stats = results["per_festival"].setdefault(
                festival_id,
                {"total": 0, "exact": 0, "errors": []},
            )
            festival_stats["total"] += 1
            if delta_days == 0:
                festival_stats["exact"] += 1
            else:
                festival_stats["errors"].append({"year": year, "delta": delta_days})

        results["per_year"][year_str] = year_stats

    total = results["total_comparisons"]
    results["accuracy_pct"] = round(100 * results["exact_matches"] / max(total, 1), 1)
    results["within_one_day_pct"] = round(
        100 * (results["exact_matches"] + results["off_by_one"]) / max(total, 1), 1
    )

    return results


def main():
    print("Running accuracy benchmark...")
    results = run_benchmark()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / "annual_accuracy_2082.json"
    report_path.write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("\n=== Accuracy Benchmark ===")
    print(f"  Total comparisons:    {results['total_comparisons']}")
    print(f"  Exact matches:        {results['exact_matches']}")
    print(f"  Off-by-1:             {results['off_by_one']}")
    print(f"  Off-by-more:          {results['off_by_more']}")
    print(f"  Calculator failed:    {results['calculator_failed']}")
    print(f"  Accuracy:             {results['accuracy_pct']}%")
    print(f"  Within +/-1 day:      {results['within_one_day_pct']}%")
    print(f"\nReport: {report_path}")

    if results["mismatches"]:
        print(f"\n  Mismatches ({len(results['mismatches'])}):")
        for mismatch in results["mismatches"][:10]:
            print(
                f"    {mismatch['festival_id']} ({mismatch['year']}): "
                f"truth={mismatch['truth']}, computed={mismatch.get('computed', 'N/A')}, "
                f"cat={mismatch['category']}"
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
