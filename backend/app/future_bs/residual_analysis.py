"""Residual analysis for future BS backtests."""

from __future__ import annotations

from typing import Any

from .backtest import backtest_model


def residual_summary(train_start: int, train_end: int, test_start: int, test_end: int) -> dict[str, Any]:
    backtest = backtest_model(train_start, train_end, test_start, test_end)
    by_month: dict[int, int] = {}
    for row in backtest["mismatch_details"]:
        month = int(row["month"])
        by_month[month] = by_month.get(month, 0) + 1
    return {
        "mode": "residual_analysis",
        "train_range": backtest["train_range"],
        "test_range": backtest["test_range"],
        "residual_count": backtest["mismatches"],
        "mismatches": backtest["mismatches"],
        "mismatches_by_month": by_month,
        "dominant_residual": "civil_assignment_boundary_sensitive" if backtest["mismatches"] else "none",
        "method_version": backtest["method_version"],
    }
