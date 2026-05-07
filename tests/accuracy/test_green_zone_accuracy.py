"""Green-zone abstention checks for future-BS predictions."""

from __future__ import annotations

from app.future_bs.backtest import backtest_model


def test_green_zone_cases_are_correct_on_current_official_holdout():
    result = backtest_model(2000, 2077, 2078, 2083, source_policy="official_only")
    metrics = result["accuracy_metrics"]

    assert metrics["green_zone_cases"] > 0
    assert metrics["green_zone_accuracy"] == 100.0
    assert metrics["green_zone_coverage"] < metrics["target_thresholds"]["green_zone_coverage"]


def test_boundary_cases_are_flagged_not_silently_green():
    result = backtest_model(2000, 2077, 2078, 2083, source_policy="official_only")
    metrics = result["accuracy_metrics"]

    assert metrics["boundary_cases"] > 0
    assert metrics["boundary_case_accuracy"] == 100.0
