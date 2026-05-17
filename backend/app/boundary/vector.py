"""Serializable boundary vector for policy decisions and membranes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.trust.field_provenance import ProvenanceMap
from app.trust.taint import AuthorityTaint, TaintFlag


@dataclass(frozen=True)
class BoundaryVector:
    authority: AuthorityTaint
    derivation: str = "computed_or_source_derived"
    temporal_scope: str = "supported_public_range"
    geography_scope: str = "np:national:default"
    conflict_state: str = "none"
    review_state: str = "required"
    reproducibility: str = "local_deterministic"
    interpretation_state: str = "literal"
    claim_boundary: str = "decision_support_not_authority"
    freshness: str = "current_snapshot"
    ignorance_state: str = "known"
    valid_for: tuple[str, ...] = ("technical_reference", "planning_support")
    flags: frozenset[TaintFlag] = field(default_factory=frozenset)
    blocked_use_cases: tuple[str, ...] = (
        "legal_final_authority",
        "tax_final_authority",
        "payroll_final_authority",
        "banking_contract_authority",
        "government_calendar_publication",
        "panchanga_final_authority",
    )
    warnings: tuple[str, ...] = ()

    @classmethod
    def from_provenance(cls, provenance: ProvenanceMap, *, ignorance_state: str = "known") -> "BoundaryVector":
        flags = frozenset(flag for field in provenance.fields.values() for flag in field.flags)
        return cls(
            authority=provenance.weakest_authority(),
            review_state="required" if flags or provenance.weakest_authority() != AuthorityTaint.STRUCTURED_OFFICIAL else "not_required",
            ignorance_state=ignorance_state,
            flags=flags,
            warnings=tuple(sorted(flag.value for flag in flags)),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "authority": self.authority.value,
            "derivation": self.derivation,
            "temporal_scope": self.temporal_scope,
            "geography_scope": self.geography_scope,
            "conflict_state": self.conflict_state,
            "review_state": self.review_state,
            "reproducibility": self.reproducibility,
            "interpretation_state": self.interpretation_state,
            "claim_boundary": self.claim_boundary,
            "freshness": self.freshness,
            "ignorance_state": self.ignorance_state,
            "valid_for": list(self.valid_for),
            "flags": sorted(flag.value for flag in self.flags),
            "blocked_use_cases": list(self.blocked_use_cases),
            "warnings": list(self.warnings),
        }
