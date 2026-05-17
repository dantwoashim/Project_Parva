"""Obligation object model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Obligation:
    obligation_id: str
    claim_type: str
    source_docket_id: str
    applicability: dict
    effective_bs: str
    deadline_bs: str
    required_action: str
    required_documents: list[str]
    boundary: dict
    proof_pack: dict

    def as_dict(self) -> dict:
        return {
            "obligation_id": self.obligation_id,
            "claim_type": self.claim_type,
            "source_docket_id": self.source_docket_id,
            "applicability": self.applicability,
            "effective_bs": self.effective_bs,
            "deadline_bs": self.deadline_bs,
            "required_action": self.required_action,
            "required_documents": self.required_documents,
            "boundary": self.boundary,
            "proof_pack": self.proof_pack,
        }
