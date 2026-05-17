"""Monotonic authority taint algebra.

Authority may degrade or stay equal. It never increases unless a review witness
performs an explicit upgrade in :mod:`app.trust.upgrade`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class AuthorityTaint(StrEnum):
    STRUCTURED_OFFICIAL = "structured_official"
    ARCHIVED_OFFICIAL = "archived_official"
    REVIEWED_INSTITUTIONAL = "reviewed_institutional"
    COMPUTED_CERTIFIED = "computed_certified"
    COMPUTED_UNCERTIFIED = "computed_uncertified"
    STATIC_REFERENCE = "static_reference"
    THIRD_PARTY_REFERENCE = "third_party_reference"
    USER_SUPPLIED = "user_supplied"
    UNKNOWN_UNVERIFIED = "unknown_unverified"


class TaintFlag(StrEnum):
    FUTURE_PROJECTED = "future_projected"
    FUZZY_INTERPRETATION = "fuzzy_interpretation"
    MANUAL_PATCH = "manual_patch"
    REVIEW_REQUIRED = "review_required"
    OVERLAY_APPLIED = "overlay_applied"
    SOURCE_CONFLICT = "source_conflict"
    POLICY_FORK = "policy_fork"
    COMMUNITY_SPECIFIC = "community_specific"
    HYPOTHETICAL = "hypothetical"
    STALE = "stale"
    SUPERSEDED = "superseded"


AUTHORITY_RANK: dict[AuthorityTaint, int] = {
    AuthorityTaint.STRUCTURED_OFFICIAL: 0,
    AuthorityTaint.ARCHIVED_OFFICIAL: 1,
    AuthorityTaint.REVIEWED_INSTITUTIONAL: 2,
    AuthorityTaint.COMPUTED_CERTIFIED: 3,
    AuthorityTaint.COMPUTED_UNCERTIFIED: 4,
    AuthorityTaint.STATIC_REFERENCE: 5,
    AuthorityTaint.THIRD_PARTY_REFERENCE: 6,
    AuthorityTaint.USER_SUPPLIED: 7,
    AuthorityTaint.UNKNOWN_UNVERIFIED: 8,
}


def authority_join(left: AuthorityTaint, right: AuthorityTaint) -> AuthorityTaint:
    """Return the weaker authority in a two-field derivation."""

    return left if AUTHORITY_RANK[left] >= AUTHORITY_RANK[right] else right


def authority_allows_upgrade(
    current: AuthorityTaint,
    target: AuthorityTaint,
) -> bool:
    """Return true when target is not stronger than current."""

    return AUTHORITY_RANK[target] >= AUTHORITY_RANK[current]


@dataclass(frozen=True)
class TaintedValue:
    value: Any
    authority: AuthorityTaint
    flags: frozenset[TaintFlag] = field(default_factory=frozenset)

    def combine(self, other: "TaintedValue", value: Any) -> "TaintedValue":
        return TaintedValue(
            value=value,
            authority=authority_join(self.authority, other.authority),
            flags=self.flags | other.flags,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "authority": self.authority.value,
            "flags": sorted(flag.value for flag in self.flags),
        }
