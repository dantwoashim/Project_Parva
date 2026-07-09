"""Residual analysis for future BS backtests."""

from __future__ import annotations

from typing import Any

from .backtest import backtest_model


def residual_summary(
    train_start: int,
    train_end: int,
    test_start: int,
    test_end: int,
    *,
    source_policy: str = "all_reference",
    model: str = "parva_solar_civil_v1",
) -> dict[str, Any]:
    backtest = backtest_model(
        train_start,
        train_end,
        test_start,
        test_end,
        source_policy=source_policy,
        model=model,
    )
    by_month: dict[int, int] = {}
    by_boundary: dict[str, int] = {}
    by_source: dict[str, int] = {}
    alternative_rules: dict[str, int] = {}
    for row in backtest["mismatch_details"]:
        month = int(row["month"])
        by_month[month] = by_month.get(month, 0) + 1
        boundary = str(row.get("boundary_risk", "unknown"))
        by_boundary[boundary] = by_boundary.get(boundary, 0) + 1
        source = str(row.get("source_type", "unknown"))
        by_source[source] = by_source.get(source, 0) + 1
        alternative = str(row.get("alternative_rule_that_would_have_worked") or "none")
        alternative_rules[alternative] = alternative_rules.get(alternative, 0) + 1
    return {
        "mode": "residual_analysis",
        "train_range": backtest["train_range"],
        "test_range": backtest["test_range"],
        "source_policy": source_policy,
        "model": model,
        "residual_count": backtest["mismatches"],
        "mismatches": backtest["mismatches"],
        "mismatches_by_month": by_month,
        "mismatches_by_boundary_risk": by_boundary,
        "mismatches_by_source_type": by_source,
        "alternative_rules_that_would_have_worked": alternative_rules,
        "mismatch_by_ingress_hour": backtest.get("mismatch_by_ingress_hour", {}),
        "mismatch_by_boundary_distance": backtest.get("mismatch_by_boundary_distance", {}),
        "accuracy_metrics": backtest.get("accuracy_metrics", {}),
        "mismatch_details": backtest.get("mismatch_details", []),
        "dominant_residual": "civil_assignment_boundary_sensitive" if backtest["mismatches"] else "none",
        "method_version": backtest["method_version"],
    }
