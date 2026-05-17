"""Phase 01 policy VM schema objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.boundary.vector import BoundaryVector
from app.trust.field_provenance import ProvenanceMap
from app.trust.taint import AuthorityTaint


@dataclass(frozen=True)
class PolicyCandidate:
    candidate_id: str
    method: str
    result: dict[str, Any]
    authority: AuthorityTaint
    field_provenance: ProvenanceMap
    boundary: BoundaryVector

    def as_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "method": self.method,
            "result": self.result,
            "authority": self.authority.value,
            "field_provenance": self.field_provenance.as_dict(),
            "boundary": self.boundary.as_dict(),
        }
