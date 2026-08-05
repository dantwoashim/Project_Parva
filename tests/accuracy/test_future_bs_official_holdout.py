"""Accuracy gates for future-BS official holdout metrics."""

from __future__ import annotations

import json
from pathlib import Path

from app.research.future_bs.backtest import backtest_model, rolling_validation
from app.research.future_bs.unified_predictor import UNIFIED_MODEL_ID

ROOT = Path(__file__).resolve().parents[2]
THRESHOLDS = ROOT / "data" / "future_bs" / "benchmarks" / "accuracy_thresholds.json"


def test_official_holdout_reports_month_level_metrics():
    result = backtest_model(2000, 2077, 2078, 2083, source_policy="official_only")

    assert result["months_tested"] == 72
    assert "overall_top1_accuracy" in result
    assert "green_zone_accuracy" in result
    assert "green_zone_coverage" in result
    assert "boundary_case_accuracy" in result
    assert result["boundary_case_accuracy"] == 100.0


def test_accuracy_claim_gate_is_locked_until_corpus_is_large_enough():
    thresholds = json.loads(THRESHOLDS.read_text(encoding="utf-8"))
    result = backtest_model(2000, 2077, 2078, 2083, source_policy="official_only")
    metrics = result["accuracy_metrics"]

    if thresholds["enforce_accuracy_gate"]:
        assert metrics["overall_top1_accuracy"] >= thresholds["overall_top1_accuracy_min"]
        assert metrics["green_zone_accuracy"] >= thresholds["green_zone_accuracy_min"]
        assert metrics["green_zone_coverage"] >= thresholds["green_zone_coverage_min"]
    else:
        assert metrics["claim_readiness"]["ready_for_99_percent_green_zone_claim"] is False
        assert thresholds["current_official_month_cases"] < thresholds["minimum_official_month_cases_for_claim"]


def test_selected_public_model_uses_rolling_time_travel_not_calibrated_replay():
    result = rolling_validation(
        2000,
        2078,
        2083,
        source_policy="official_only",
        training_source_policy="source_stratified",
        model=UNIFIED_MODEL_ID,
    )

    assert result["exact_matches"] == 72
    assert result["leakage_safe"] is True
    assert all(run["train_end"] == run["test_start"] - 1 for run in result["runs"])
