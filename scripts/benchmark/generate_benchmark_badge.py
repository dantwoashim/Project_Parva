#!/usr/bin/env python3
"""Generate public benchmark badge and frontend summary assets."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
COMPARISON_JSON = ROOT / "public-benchmark" / "results" / "comparison.json"
BENCHMARK_SVG = ROOT / "public-benchmark" / "results" / "benchmark.svg"
SUMMARY_JSON = ROOT / "public-benchmark" / "results" / "benchmark-summary.json"
FRONTEND_SUMMARY_JSON = ROOT / "frontend" / "src" / "data" / "benchmarkSummary.json"


def _load_comparison() -> dict[str, Any]:
    if not COMPARISON_JSON.exists():
        raise FileNotFoundError(
            f"{COMPARISON_JSON} is missing. Run public-benchmark/runners/compare_results.py first."
        )
    return json.loads(COMPARISON_JSON.read_text(encoding="utf-8"))


def _summary(comparison: dict[str, Any]) -> dict[str, Any]:
    source_mtime = datetime.fromtimestamp(COMPARISON_JSON.stat().st_mtime, UTC).isoformat()
    parva_summary = comparison.get("parva_summary", {})
    review_gate = comparison.get("review_gate_performance", {})
    return {
        "parva_score_percent": comparison["parva_score_percent"],
        "static_score_percent": comparison["static_score_percent"],
        "score_gap_percent": comparison["score_gap_percent"],
        "task_count": parva_summary.get("total", 0),
        "generated_at": source_mtime,
        "review_gate_performance": review_gate,
        "category_breakdown": comparison.get("category_breakdown", {}),
        "claim_boundary": "technical_benchmark_not_authority",
        "source": "public-benchmark/results/comparison.json",
    }


def _badge_svg(summary: dict[str, Any]) -> str:
    label = "Parva benchmark"
    value = f"{summary['parva_score_percent']}% vs static {summary['static_score_percent']}%"
    label_width = 116
    value_width = max(150, 8 * len(value) + 22)
    total_width = label_width + value_width
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="24" role="img" aria-label="{escape(label)} {escape(value)}">
  <title>{escape(label)} {escape(value)}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#fff" stop-opacity=".08"/>
    <stop offset="1" stop-opacity=".08"/>
  </linearGradient>
  <clipPath id="r"><rect width="{total_width}" height="24" rx="4"/></clipPath>
  <g clip-path="url(#r)">
    <rect width="{label_width}" height="24" fill="#2f3a3a"/>
    <rect x="{label_width}" width="{value_width}" height="24" fill="#0f7b63"/>
    <rect width="{total_width}" height="24" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,sans-serif" font-size="11">
    <text x="{label_width / 2}" y="15" fill="#010101" fill-opacity=".25">{escape(label)}</text>
    <text x="{label_width / 2}" y="14">{escape(label)}</text>
    <text x="{label_width + value_width / 2}" y="15" fill="#010101" fill-opacity=".25">{escape(value)}</text>
    <text x="{label_width + value_width / 2}" y="14">{escape(value)}</text>
  </g>
</svg>
"""


def main() -> int:
    comparison = _load_comparison()
    summary = _summary(comparison)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    FRONTEND_SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)
    FRONTEND_SUMMARY_JSON.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    BENCHMARK_SVG.write_text(_badge_svg(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
