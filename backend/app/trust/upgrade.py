"""Explicit review witnesses for authority upgrades."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from app.trust.taint import AUTHORITY_RANK, AuthorityTaint, TaintedValue


@dataclass(frozen=True)
class ReviewWitness:
    scope: dict[str, str]
    from_taint: AuthorityTaint
    to_taint: AuthorityTaint
    reviewer: str
    checklist_hash: str
    signature: str

    @classmethod
    def create(
        cls,
        *,
        scope: dict[str, str],
        from_taint: AuthorityTaint,
        to_taint: AuthorityTaint,
        reviewer: str,
        checklist_hash: str,
    ) -> "ReviewWitness":
        payload = {
            "scope": scope,
            "from_taint": from_taint.value,
            "to_taint": to_taint.value,
            "reviewer": reviewer,
            "checklist_hash": checklist_hash,
        }
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return cls(
            scope=scope,
            from_taint=from_taint,
            to_taint=to_taint,
            reviewer=reviewer,
            checklist_hash=checklist_hash,
            signature=f"review-sha256:{digest}",
        )

    def validates(self) -> bool:
        return self.signature.startswith("review-sha256:") and bool(self.reviewer)

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": "review_witness",
            "scope": dict(self.scope),
            "from_taint": self.from_taint.value,
            "to_taint": self.to_taint.value,
            "reviewer": self.reviewer,
            "checklist_hash": self.checklist_hash,
            "signature": self.signature,
        }


def apply_review_upgrade(value: TaintedValue, target: AuthorityTaint, witness: ReviewWitness) -> TaintedValue:
    """Upgrade authority only when a witness explicitly authorizes that edge."""

    if AUTHORITY_RANK[target] >= AUTHORITY_RANK[value.authority]:
        return TaintedValue(value=value.value, authority=target, flags=value.flags)
    if witness.from_taint != value.authority or witness.to_taint != target or not witness.validates():
        raise ValueError("authority upgrade requires a matching valid review witness")
    return TaintedValue(value=value.value, authority=target, flags=value.flags)
