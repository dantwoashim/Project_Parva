"""Conformance capsule schema."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConformanceCapsule:
    capsule_id: str
    workflow: str
    cases: list[dict]
    claim_boundary: str = "conformance_report_not_certification"

    def as_dict(self) -> dict:
        return {
            "capsule_id": self.capsule_id,
            "workflow": self.workflow,
            "cases": self.cases,
            "claim_boundary": self.claim_boundary,
        }
