"""Constraint relaxation suggestions."""

from __future__ import annotations


def suggest_relaxations(unsat_core: list[str]) -> list[str]:
    suggestions = []
    if "not_enough_working_days" in unsat_core:
        suggestions.extend(["reduce_count", "extend_date_range"])
    return suggestions or ["manual_review"]
