"""Canonical public-safe boundary labels."""

from __future__ import annotations

from enum import StrEnum


class BoundaryLabel(StrEnum):
    DECISION_SUPPORT_NOT_AUTHORITY = "decision_support_not_authority"
    COMPUTED_NOT_OFFICIAL = "computed_prediction_not_official"
    STATIC_REFERENCE_NOT_AUTHORITY = "static_lookup_reference_not_authority"
    BRANCH_SET_REQUIRES_REVIEW = "branch_set_requires_review"
    LOCAL_REPRODUCTION_ONLY = "local_reproduction_not_live_sla"


FORBIDDEN_AUTHORITY_CLAIMS = (
    "government_authority",
    "legal_authority",
    "tax_authority",
    "banking_authority",
    "payroll_authority",
    "religious_authority",
    "official_future_date_authority",
)


def no_authority_boundary(label: BoundaryLabel) -> dict[str, object]:
    return {
        "claim_boundary": label.value,
        "not_authority": True,
        "forbidden_claims": list(FORBIDDEN_AUTHORITY_CLAIMS),
    }
