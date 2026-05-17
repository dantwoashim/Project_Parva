"""Field-level provenance model integrated with authority taint."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.trust.taint import AuthorityTaint, TaintFlag, authority_join


@dataclass(frozen=True)
class FieldProvenance:
    field_path: str
    authority: AuthorityTaint
    derivation: str
    source_docket_id: str | None = None
    witness_ids: tuple[str, ...] = ()
    policy_id: str | None = None
    review_state: str = "unreviewed"
    flags: frozenset[TaintFlag] = field(default_factory=frozenset)

    def as_dict(self) -> dict[str, Any]:
        return {
            "field_path": self.field_path,
            "authority": self.authority.value,
            "derivation": self.derivation,
            "source_docket_id": self.source_docket_id,
            "witness_ids": list(self.witness_ids),
            "policy_id": self.policy_id,
            "review_state": self.review_state,
            "flags": sorted(flag.value for flag in self.flags),
        }


@dataclass(frozen=True)
class ProvenanceMap:
    fields: dict[str, FieldProvenance]

    def weakest_authority(self) -> AuthorityTaint:
        if not self.fields:
            return AuthorityTaint.UNKNOWN_UNVERIFIED
        authorities = [field.authority for field in self.fields.values()]
        weakest = authorities[0]
        for authority in authorities[1:]:
            weakest = authority_join(weakest, authority)
        return weakest

    def require_all_fields(self, result: dict[str, Any]) -> None:
        missing = sorted(key for key in result if key not in self.fields)
        if missing:
            raise ValueError(f"missing field provenance for: {', '.join(missing)}")

    def require_source_backed_dockets(self) -> None:
        source_backed = {
            AuthorityTaint.STRUCTURED_OFFICIAL,
            AuthorityTaint.ARCHIVED_OFFICIAL,
            AuthorityTaint.REVIEWED_INSTITUTIONAL,
        }
        missing = sorted(
            path
            for path, provenance in self.fields.items()
            if provenance.authority in source_backed and not provenance.source_docket_id
        )
        if missing:
            raise ValueError(f"source-backed fields lack source docket lineage: {', '.join(missing)}")

    def as_dict(self) -> dict[str, Any]:
        return {path: provenance.as_dict() for path, provenance in sorted(self.fields.items())}
