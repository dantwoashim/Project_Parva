"""Week 29 tests for evaluation_v4 summary logic."""

from __future__ import annotations

from backend.tools.evaluate_v4 import EvalRow, summarize


def test_summarize_groups_by_rule_and_festival():
    rows = [
        EvalRow("dashain", 2026, "2026-10-10", "2026-10-10", True, 0, "src", "", "lunar", "match"),
        EvalRow("dashain", 2027, "2027-10-01", "2027-10-02", True, 1, "src", "", "lunar", "match"),
        EvalRow("maghe-sankranti", 2026, "2026-01-14", None, False, None, "src", "", "solar", "missing_result"),
    ]

    summary = summarize(rows)
    assert summary["total"] == 3
    assert summary["passed"] == 2
    assert summary["by_festival"]["dashain"]["pass_rate"] == 100.0
    assert summary["by_rule"]["solar"]["pass_rate"] == 0.0
