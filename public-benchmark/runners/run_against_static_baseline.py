#!/usr/bin/env python3
"""Naive static-table baseline for benchmark comparison."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validate_benchmark import validate_benchmark_document  # noqa: E402

RESULTS_PATH = ROOT / "results" / "latest-static-baseline.json"
WEIGHTS = {
    "correctness": 40,
    "source_awareness": 20,
    "uncertainty_handling": 20,
    "review_gate_behavior": 10,
    "machine_readable_structure": 10,
}


def _load_benchmark() -> dict:
    benchmark = json.loads((ROOT / "benchmark.json").read_text(encoding="utf-8"))
    issues = validate_benchmark_document(benchmark)
    if issues:
        raise ValueError("; ".join(issues))
    return benchmark


def _result_for_task(task: dict) -> dict:
    category = task["category"]
    supported = category in {
        "bs_ad_conversion",
        "ad_bs_conversion",
        "valid_invalid_bs_dates",
        "invalid_bs_dates",
    }
    signals = {
        "correctness": supported,
        "source_awareness": False,
        "uncertainty_handling": False,
        "review_gate_behavior": False,
        "machine_readable_structure": True,
    }
    return {
        "id": task["id"],
        "category": category,
        "status": "pass" if supported else "unsupported",
        "signals": signals,
        "score": sum(weight for key, weight in WEIGHTS.items() if signals[key]),
    }


def run_static_baseline() -> dict:
    benchmark = _load_benchmark()
    results = [_result_for_task(task) for task in benchmark["tasks"]]
    score = sum(item["score"] for item in results)
    max_score = len(results) * sum(WEIGHTS.values())
    return {
        "runner": "static_baseline",
        "schema_version": benchmark["schema_version"],
        "summary": {
            "total": len(results),
            "passed": sum(1 for item in results if item["status"] == "pass"),
            "unsupported": sum(1 for item in results if item["status"] == "unsupported"),
            "score": score,
            "max_score": max_score,
            "score_percent": round((score / max_score) * 100.0, 2) if max_score else 0.0,
        },
        "results": results,
    }


def main() -> int:
    report = run_static_baseline()
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
