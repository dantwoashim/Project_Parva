#!/usr/bin/env python3
"""Validate the public Nepali Time Reliability Benchmark."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
BENCHMARK_PATH = ROOT / "benchmark.json"
SCHEMA_PATH = ROOT / "schema.json"
REQUIRED_SCORING = {
    "correctness": 40,
    "source_awareness": 20,
    "uncertainty_handling": 20,
    "review_gate_behavior": 10,
    "machine_readable_structure": 10,
}
FORBIDDEN_AUTHORITY_BOUNDARIES = {
    "official_future_date",
    "government_authority",
    "legal_authority",
    "banking_authority",
    "payroll_authority",
    "tax_authority",
}


def load_benchmark(path: Path = BENCHMARK_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_benchmark_document(benchmark: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    tasks = benchmark.get("tasks")
    scoring = benchmark.get("scoring")

    if not isinstance(benchmark.get("schema_version"), str) or not benchmark["schema_version"]:
        issues.append("schema_version is required")
    if not isinstance(benchmark.get("claim_boundary"), str) or "authority" not in benchmark["claim_boundary"]:
        issues.append("claim_boundary must make the authority boundary explicit")
    if scoring != REQUIRED_SCORING:
        issues.append(f"scoring must equal {REQUIRED_SCORING}")
    if not isinstance(tasks, list) or len(tasks) < 30:
        issues.append("tasks must contain at least 30 public-safe tasks")
        return issues

    ids = [task.get("id") for task in tasks if isinstance(task, dict)]
    duplicates = sorted(key for key, count in Counter(ids).items() if key and count > 1)
    if duplicates:
        issues.append(f"duplicate task ids: {', '.join(duplicates)}")

    scoring_keys = set(REQUIRED_SCORING)
    for index, task in enumerate(tasks):
        prefix = f"tasks[{index}]"
        if not isinstance(task, dict):
            issues.append(f"{prefix} must be an object")
            continue
        for key in ("id", "category", "input", "expected", "public_safe", "authority_boundary", "scoring_dimensions"):
            if key not in task:
                issues.append(f"{prefix}.{key} is required")
        if task.get("public_safe") is not True:
            issues.append(f"{prefix}.public_safe must be true")
        if not isinstance(task.get("input"), dict):
            issues.append(f"{prefix}.input must be an object")
        if not isinstance(task.get("expected"), dict):
            issues.append(f"{prefix}.expected must be an object")
        boundary = str(task.get("authority_boundary") or "")
        if not boundary or boundary in FORBIDDEN_AUTHORITY_BOUNDARIES:
            issues.append(f"{prefix}.authority_boundary is unsafe")
        dimensions = task.get("scoring_dimensions")
        if not isinstance(dimensions, list) or set(dimensions) != scoring_keys:
            issues.append(f"{prefix}.scoring_dimensions must cover all scoring keys")
        if task.get("category") == "future_bs_unsupported_review_required":
            expected = task.get("expected", {})
            if expected.get("publication_status") == "computed_prediction_not_official" and expected.get("review_required") is not True:
                issues.append(f"{prefix} Future-BS computed predictions must require review")
            if expected.get("exact_predictions_public") is not None and expected.get("exact_predictions_public") is not False:
                issues.append(f"{prefix} must not expect public exact Future-BS predictions")

    return issues


def validate_benchmark_file(path: Path = BENCHMARK_PATH) -> list[str]:
    if not SCHEMA_PATH.exists():
        return ["schema.json is missing"]
    return validate_benchmark_document(load_benchmark(path))


def main() -> int:
    issues = validate_benchmark_file()
    if issues:
        for issue in issues:
            print(f"[benchmark] {issue}")
        return 1
    benchmark = load_benchmark()
    print(
        json.dumps(
            {
                "ok": True,
                "tasks": len(benchmark["tasks"]),
                "schema": "public-benchmark/schema.json",
                "claim_boundary": benchmark["claim_boundary"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
