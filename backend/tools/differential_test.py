"""
Differential Test Runner
=========================

Compare Parva output against external reference data to detect
discrepancies and track accuracy over time.

Usage:
    python -m backend.tools.differential_test --year 2025 --output results/diff_2025.json
"""

import json
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.calendar.calculator_v2 import calculate_festival_v2, list_festivals_v2


# ── Known External References ─────────────────────────────────────
# These are manually verified festival dates from published sources
REFERENCE_DATA = {
    2025: {
        "dashain": {"start": "2025-10-02", "source": "Nepal Govt Gazette"},
        "tihar": {"start": "2025-10-20", "source": "Nepal Govt Gazette"},
        "holi": {"start": "2025-03-14", "source": "drikpanchang.com"},
        "chhath": {"start": "2025-10-26", "source": "drikpanchang.com"},
        "maghe_sankranti": {"start": "2025-01-14", "source": "drikpanchang.com"},
    },
    2026: {
        "dashain": {"start": "2026-09-21", "source": "Projected"},
        "tihar": {"start": "2026-11-08", "source": "Projected"},
        "holi": {"start": "2026-03-03", "source": "Projected"},
        "maghe_sankranti": {"start": "2026-01-14", "source": "Projected"},
    },
}


def run_differential_test(year: int) -> Dict:
    """
    Compare Parva calculations against reference data for a year.

    Returns a diff report with matches, mismatches, and missing festivals.
    """
    reference = REFERENCE_DATA.get(year, {})
    all_festivals = list_festivals_v2()

    results = {
        "year": year,
        "matches": [],
        "mismatches": [],
        "parva_only": [],
        "reference_only": [],
        "total_compared": 0,
        "accuracy": 0.0,
    }

    # Compare each reference entry
    for fid, ref in reference.items():
        ref_date = ref["start"]
        parva_result = calculate_festival_v2(fid, year)

        if parva_result is None:
            results["reference_only"].append({
                "festival_id": fid,
                "reference_date": ref_date,
                "source": ref["source"],
                "parva_status": "not_found",
            })
            continue

        parva_date = parva_result.start_date.isoformat()
        results["total_compared"] += 1

        if parva_date == ref_date:
            results["matches"].append({
                "festival_id": fid,
                "date": parva_date,
                "source": ref["source"],
                "method": parva_result.method,
            })
        else:
            results["mismatches"].append({
                "festival_id": fid,
                "parva_date": parva_date,
                "reference_date": ref_date,
                "source": ref["source"],
                "method": parva_result.method,
                "delta_days": (parva_result.start_date - date.fromisoformat(ref_date)).days,
            })

    # Festivals in Parva but not in reference
    for fid in all_festivals:
        if fid not in reference:
            result = calculate_festival_v2(fid, year)
            if result:
                results["parva_only"].append({
                    "festival_id": fid,
                    "parva_date": result.start_date.isoformat(),
                    "method": result.method,
                })

    # Calculate accuracy
    if results["total_compared"] > 0:
        results["accuracy"] = len(results["matches"]) / results["total_compared"]

    return results


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Parva Differential Test Runner")
    parser.add_argument("--year", type=int, default=2025, help="Year to test")
    parser.add_argument("--output", type=str, default=None, help="Output JSON path")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    results = run_differential_test(args.year)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)

    # Print summary
    print(f"=== Differential Test: {args.year} ===")
    print(f"Compared: {results['total_compared']}")
    print(f"Matches:  {len(results['matches'])}")
    print(f"Mismatches: {len(results['mismatches'])}")
    print(f"Accuracy: {results['accuracy']*100:.1f}%")

    if args.verbose and results["mismatches"]:
        print("\nMismatches:")
        for m in results["mismatches"]:
            print(f"  {m['festival_id']}: Parva={m['parva_date']}, Ref={m['reference_date']} ({m['source']})")


if __name__ == "__main__":
    main()
