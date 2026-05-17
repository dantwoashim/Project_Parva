"""Policy lenses expose task-specific views without mutating canonical truth."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PolicyLens:
    lens_id: str
    purpose: str
    allowed_fields: tuple[str, ...]
    boundary_note: str = "lens_view_not_canonical_mutation"

    def apply(self, claim: dict[str, Any]) -> dict[str, Any]:
        projected = {field: claim[field] for field in self.allowed_fields if field in claim}
        return {
            "kind": "policy_lens_view",
            "lens_id": self.lens_id,
            "purpose": self.purpose,
            "result": projected,
            "boundary_note": self.boundary_note,
            "canonical_unchanged": True,
        }


PAYROLL_REVIEW_LENS = PolicyLens(
    lens_id="payroll_review@v1",
    purpose="show only date, working-day, holiday, and review fields",
    allowed_fields=("bs_date", "ad_date", "working_day", "holiday", "review_required", "boundary"),
)
