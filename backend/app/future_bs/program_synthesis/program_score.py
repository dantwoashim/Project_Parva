"""Candidate rule scoring for a bounded DSL search."""

from __future__ import annotations

from typing import Any

from .rule_dsl import RuleProgram


def score_program(program: RuleProgram, features: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(features) or 1
    valid = sum(1 for row in features if int(row["month_length"]) in {29, 30, 31, 32})
    conflicts = sum(1 for row in features if row.get("manual_review_required"))
    complexity_penalty = 0.01 * program.complexity
    score = valid / total - conflicts / total - complexity_penalty
    return {
        **program.payload(),
        "validity_rate": round(valid / total, 6),
        "manual_review_rate": round(conflicts / total, 6),
        "score": round(score, 6),
    }
