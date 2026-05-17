from __future__ import annotations

import json
from pathlib import Path

from scripts.benchmark.generate_benchmark_badge import (
    BENCHMARK_SVG,
    COMPARISON_JSON,
    SUMMARY_JSON,
    main,
)


def test_benchmark_badge_generation_outputs_public_assets():
    assert main() == 0

    summary = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))
    comparison = json.loads(COMPARISON_JSON.read_text(encoding="utf-8"))
    svg = BENCHMARK_SVG.read_text(encoding="utf-8")

    assert summary["parva_score_percent"] == comparison["parva_score_percent"]
    assert summary["static_score_percent"] == comparison["static_score_percent"]
    assert summary["task_count"] == comparison["parva_summary"]["total"]
    assert summary["claim_boundary"] == "technical_benchmark_not_authority"
    assert "Parva benchmark" in svg
    assert f"{comparison['parva_score_percent']}%" in svg
    assert Path("frontend/src/data/benchmarkSummary.json").exists()
