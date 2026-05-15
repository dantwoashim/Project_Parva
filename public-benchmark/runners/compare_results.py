#!/usr/bin/env python3
"""Compare Parva benchmark results against the static baseline."""

from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUNNERS = ROOT / "runners"
RESULTS = ROOT / "results"
PARVA_RESULTS = RESULTS / "latest-parva.json"
STATIC_RESULTS = RESULTS / "latest-static-baseline.json"
COMPARISON_JSON = RESULTS / "comparison.json"
COMPARISON_MD = RESULTS / "comparison.md"


def _run_if_missing(path: Path, command: list[str]) -> None:
    if path.exists():
        return
    result = subprocess.run(command, cwd=ROOT.parent, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"{' '.join(command)} failed with {result.returncode}: {result.stderr or result.stdout}")


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _category_breakdown(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = defaultdict(lambda: {"tasks": 0, "score": 0, "max_score": 0, "blocked": 0, "failed": 0})
    for result in report.get("results", []):
        category = str(result["category"])
        bucket = buckets[category]
        bucket["tasks"] += 1
        bucket["score"] += int(result.get("score", 0))
        bucket["max_score"] += 100
        bucket["blocked"] += 1 if result.get("status") == "blocked" else 0
        bucket["failed"] += 1 if result.get("status") == "fail" else 0
    for bucket in buckets.values():
        bucket["score_percent"] = round((bucket["score"] / bucket["max_score"]) * 100.0, 2) if bucket["max_score"] else 0.0
    return dict(sorted(buckets.items()))


def compare(parva: dict[str, Any], static: dict[str, Any]) -> dict[str, Any]:
    parva_by_id = {item["id"]: item for item in parva.get("results", [])}
    static_by_id = {item["id"]: item for item in static.get("results", [])}
    gaps = []
    for task_id, parva_result in parva_by_id.items():
        baseline_result = static_by_id.get(task_id, {"score": 0})
        gaps.append(
            {
                "id": task_id,
                "category": parva_result["category"],
                "parva_score": parva_result.get("score", 0),
                "static_score": baseline_result.get("score", 0),
                "gap": int(parva_result.get("score", 0)) - int(baseline_result.get("score", 0)),
                "parva_status": parva_result.get("status"),
            }
        )
    gaps.sort(key=lambda item: (item["gap"], item["id"]), reverse=True)
    unsupported = [item for item in parva.get("results", []) if item.get("status") in {"blocked", "unsupported"}]
    review_total = 0
    review_hits = 0
    for item in parva.get("results", []):
        signals = item.get("signals", {})
        if item.get("category") in {"future_bs_unsupported_review_required", "payroll_repayment_review_gates"}:
            review_total += 1
            review_hits += 1 if signals.get("review_gate_behavior") else 0

    return {
        "parva_score_percent": parva["summary"]["score_percent"],
        "static_score_percent": static["summary"]["score_percent"],
        "score_gap_percent": round(parva["summary"]["score_percent"] - static["summary"]["score_percent"], 2),
        "parva_summary": parva["summary"],
        "static_summary": static["summary"],
        "category_breakdown": {
            "parva": _category_breakdown(parva),
            "static_baseline": _category_breakdown(static),
        },
        "biggest_positive_gaps": gaps[:10],
        "unsupported_tasks": [{"id": item["id"], "category": item["category"], "status": item.get("status")} for item in unsupported],
        "review_gate_performance": {
            "tasks": review_total,
            "passed": review_hits,
            "score_percent": round((review_hits / review_total) * 100.0, 2) if review_total else 0.0,
        },
    }


def _write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Benchmark Comparison",
        "",
        f"- Parva score: {report['parva_score_percent']}%",
        f"- Static baseline score: {report['static_score_percent']}%",
        f"- Gap: {report['score_gap_percent']} percentage points",
        f"- Review gate performance: {report['review_gate_performance']['passed']}/{report['review_gate_performance']['tasks']}",
        f"- Unsupported tasks: {len(report['unsupported_tasks'])}",
        "",
        "## Biggest Gaps",
        "",
    ]
    for item in report["biggest_positive_gaps"]:
        lines.append(f"- `{item['id']}` ({item['category']}): Parva {item['parva_score']} vs static {item['static_score']}")
    COMPARISON_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    _run_if_missing(STATIC_RESULTS, [sys.executable, str(RUNNERS / "run_against_static_baseline.py")])
    _run_if_missing(PARVA_RESULTS, [sys.executable, str(RUNNERS / "run_against_parva.py")])
    report = compare(_load(PARVA_RESULTS), _load(STATIC_RESULTS))
    RESULTS.mkdir(parents=True, exist_ok=True)
    COMPARISON_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
