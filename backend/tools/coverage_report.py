#!/usr/bin/env python3
"""
Coverage report for override-backed accuracy.

Shows how many festival-year pairs are covered by authoritative overrides.
"""

import argparse
import json
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent.parent / "app" / "calendar"
OVERRIDES_PATH = ROOT / "ground_truth_overrides.json"
RULES_PATH = ROOT / "festival_rules_v3.json"


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_coverage(year_start: int, year_end: int):
    overrides = load_json(OVERRIDES_PATH)
    rules = load_json(RULES_PATH)
    festivals = sorted(rules.get("festivals", {}).keys())

    total = 0
    covered = 0
    missing = []

    for year in range(year_start, year_end + 1):
        y = str(year)
        for fid in festivals:
            total += 1
            if y in overrides and fid in overrides[y]:
                covered += 1
            else:
                missing.append((year, fid))

    pct = (covered / total * 100) if total else 0.0
    return {
        "year_start": year_start,
        "year_end": year_end,
        "festivals": len(festivals),
        "total_pairs": total,
        "covered_pairs": covered,
        "coverage_pct": round(pct, 2),
        "missing": missing,
    }


def main():
    parser = argparse.ArgumentParser(description="Override coverage report")
    parser.add_argument("--start", type=int, default=2025, help="Start year")
    parser.add_argument("--end", type=int, default=2027, help="End year")
    parser.add_argument("--output", "-o", help="Optional JSON output path")
    args = parser.parse_args()

    report = compute_coverage(args.start, args.end)

    print("Override Coverage Report")
    print(f"Years: {report['year_start']}–{report['year_end']}")
    print(f"Festivals: {report['festivals']}")
    print(f"Covered: {report['covered_pairs']}/{report['total_pairs']} ({report['coverage_pct']}%)")
    print(f"Missing pairs: {len(report['missing'])}")

    if args.output:
        out_path = Path(args.output)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Saved report: {out_path}")


if __name__ == "__main__":
    main()
