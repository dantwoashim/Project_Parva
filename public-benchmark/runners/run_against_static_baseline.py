#!/usr/bin/env python3
"""Naive static-table baseline for benchmark comparison."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEIGHTS = {
    "correctness": 40,
    "source_awareness": 20,
    "uncertainty_handling": 20,
    "review_gate_behavior": 10,
    "machine_readable_structure": 10,
}


def _load_benchmark() -> dict:
    return json.loads((ROOT / "benchmark.json").read_text(encoding="utf-8"))


def _result_for_task(task: dict) -> dict:
    category = task["category"]
    supported = category in {"bs_ad_conversion", "ad_bs_conversion", "valid_invalid_bs_dates"}
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
    print(json.dumps(run_static_baseline(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
