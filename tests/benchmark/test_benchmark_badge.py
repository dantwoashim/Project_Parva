from __future__ import annotations

import json
from pathlib import Path

from scripts.benchmark.generate_benchmark_badge import BENCHMARK_SVG, SUMMARY_JSON, main


def test_benchmark_badge_generation_outputs_public_assets():
    assert main() == 0

    summary = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))
    svg = BENCHMARK_SVG.read_text(encoding="utf-8")

    assert summary["parva_score_percent"] == 89.47
    assert summary["static_score_percent"] == 20.53
    assert summary["task_count"] == 38
    assert summary["claim_boundary"] == "technical_benchmark_not_authority"
    assert "Parva benchmark" in svg
    assert "89.47%" in svg
    assert Path("frontend/src/data/benchmarkSummary.json").exists()
