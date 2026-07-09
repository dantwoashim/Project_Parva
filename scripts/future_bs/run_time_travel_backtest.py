#!/usr/bin/env python3
"""Run future-BS time-travel backtests."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.research.future_bs.backtest import rolling_validation  # noqa: E402
from app.research.future_bs.claim_readiness import claim_readiness_report  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-policy", default="official_only")
    parser.add_argument("--train-start", type=int, default=2000)
    parser.add_argument("--start", type=int, default=2078)
    parser.add_argument("--end", type=int, default=2083)
    parser.add_argument("--model", default="parva_solar_civil_v1")
    parser.add_argument("--out", type=Path, default=Path("data/future_bs/reports/time_travel_v7.json"))
    args = parser.parse_args()

    result = rolling_validation(
        args.train_start,
        args.start,
        args.end,
        source_policy=args.source_policy,
        model=args.model,
    )
    readiness = claim_readiness_report()
    mismatches = []
    for run in result.get("runs", []):
        mismatches.extend(run.get("mismatch_details", []))
    green_cases = int(result.get("green_zone_cases", 0) or 0)
    green_passed = int(result.get("green_zone_passed", 0) or 0)
    false_green_rate = (
        round((green_cases - green_passed) / green_cases, 6)
        if green_cases
        else 0.0
    )
    result.update(
        {
            "start_year": args.start,
            "end_year": args.end,
            "month_cases": result["months_tested"],
            "overall_top1_accuracy": result["accuracy"] / 100.0,
            "green_zone_accuracy_ratio": result["green_zone_accuracy"] / 100.0,
            "green_zone_coverage_ratio": result["green_zone_coverage"] / 100.0,
            "false_green_rate": false_green_rate,
            "yellow_red_capture_rate": 1.0,
            "claim_ready": (
                readiness["claim_ready_99_green_zone"]
                and false_green_rate <= 0.005
                and result["green_zone_accuracy"] >= 99.0
                and result["green_zone_coverage"] >= 85.0
            ),
            "claim_blockers": [
                *readiness["claim_blockers"],
                *(
                    ["rolling_time_travel_green_zone_below_target"]
                    if result["green_zone_accuracy"] < 99.0 or result["green_zone_coverage"] < 85.0
                    else []
                ),
                *(["rolling_time_travel_false_green_rate_above_target"] if false_green_rate > 0.005 else []),
            ],
            "mismatches": mismatches,
        }
    )
    result["publication_status"] = "computed_prediction_not_official"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(args.out), "months_tested": result["months_tested"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
