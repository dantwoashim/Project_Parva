"""External witness submission schema."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WitnessSubmission:
    submitter_id: str
    claim: dict
    source_docket: dict
    proof_pack: dict
    signature: str | None
    authority_scope: str
    status: str = "pending_untrusted"

    def validate(self) -> None:
        if self.status != "pending_untrusted":
            raise ValueError("external witnesses must start pending_untrusted")
        if self.authority_scope in {"national_canonical", "legal_final"}:
            raise ValueError("external witness cannot claim canonical/final authority")

    def as_dict(self) -> dict:
        self.validate()
        return {
            "submitter_id": self.submitter_id,
            "claim": self.claim,
            "source_docket": self.source_docket,
            "proof_pack": self.proof_pack,
            "signature": self.signature,
            "authority_scope": self.authority_scope,
            "status": self.status,
        }
