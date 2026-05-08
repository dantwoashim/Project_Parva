"""Tiny DSL for explainable month-start decision programs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RuleProgram:
    name: str
    description: str
    complexity: int

    def payload(self) -> dict[str, object]:
        return {
            "name": self.name,
            "description": self.description,
            "complexity": self.complexity,
        }


CANDIDATE_PROGRAMS = [
    RuleProgram("source_weighted_lattice", "Use source-weighted month starts and year-total constraints.", 2),
    RuleProgram("recent_month_mode", "Use recent verified/publisher mode by month.", 1),
    RuleProgram("weak_all_witness_mode", "Use all witnesses with weak-source fusion.", 3),
]
