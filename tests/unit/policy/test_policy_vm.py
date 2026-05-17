from __future__ import annotations

from app.boundary.vector import BoundaryVector
from app.policy.schema import PolicyCandidate
from app.policy.vm import PolicyVM
from app.trust.field_provenance import FieldProvenance, ProvenanceMap
from app.trust.taint import AuthorityTaint, TaintFlag


def _candidate(candidate_id: str, authority: AuthorityTaint) -> PolicyCandidate:
    provenance = ProvenanceMap(
        {
            "total_days": FieldProvenance(
                "total_days",
                authority,
                "computed" if authority != AuthorityTaint.STATIC_REFERENCE else "static_lookup",
                flags=frozenset({TaintFlag.REVIEW_REQUIRED})
                if authority == AuthorityTaint.STATIC_REFERENCE
                else frozenset(),
            )
        }
    )
    return PolicyCandidate(
        candidate_id=candidate_id,
        method=candidate_id,
        result={"total_days": 365 if authority != AuthorityTaint.STATIC_REFERENCE else 367},
        authority=authority,
        field_provenance=provenance,
        boundary=BoundaryVector.from_provenance(provenance),
    )


def test_policy_vm_rejects_static_reference_when_computed_candidate_exists() -> None:
    decision = PolicyVM().select(
        [
            _candidate("static_reference", AuthorityTaint.STATIC_REFERENCE),
            _candidate("solar_civil", AuthorityTaint.COMPUTED_UNCERTIFIED),
        ]
    )
    assert decision.selected.candidate_id == "solar_civil"
    assert decision.rejected[0]["candidate_id"] == "static_reference"
    assert decision.boundary.authority == AuthorityTaint.COMPUTED_UNCERTIFIED
