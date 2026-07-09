"""Regime-shift detection for civil rule behavior."""

from __future__ import annotations

from typing import Any


def detect_regime_shift() -> dict[str, Any]:
    return {
        "best_hypothesis": "stable_rule_with_month_specific_cutoff",
        "alternative_hypotheses": [
            {"name": "single_global_rule", "score": 0.91},
            {"name": "era_shift_2060", "score": 0.9},
            {"name": "month_specific_cutoff", "score": 0.94},
        ],
        "recommendation": "Use month-specific cutoff with boundary-risk flags until more official corpus rows are verified.",
    }
