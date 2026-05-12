"""Public-safe data models for future-BS risk posture."""

from __future__ import annotations

from dataclasses import dataclass, field

from .labels import PUBLICATION_STATUS, RiskLabel
from .reason_codes import RiskReasonCode


@dataclass(frozen=True)
class FutureBSRiskInput:
    """Input assumption for risk review.

    The month length is used only to classify the external assumption. Public
    output intentionally does not return corrected future values.
    """

    bs_year: int
    bs_month: int
    month_length: int
    source_policy: str = "external_shadow_review"
    synthetic_example: bool = False


@dataclass(frozen=True)
class FutureBSRiskAssessment:
    """Public-safe risk assessment shape."""

    bs_year: int
    bs_month: int
    risk_label: RiskLabel
    reason_codes: list[RiskReasonCode]
    source_policy: str
    boundary_sensitive: bool = False
    review_required: bool = False
    high_risk: bool = False
    corrected_value_included: bool = False
    publication_status: str = PUBLICATION_STATUS
    notes: list[str] = field(default_factory=list)

    def to_public_dict(self) -> dict[str, object]:
        """Serialize without returning corrected future month values."""

        return {
            "bs_year": self.bs_year,
            "bs_month": self.bs_month,
            "publication_status": self.publication_status,
            "risk_label": self.risk_label.value,
            "corrected_value_included": self.corrected_value_included,
            "reason_codes": [reason.value for reason in self.reason_codes],
            "source_policy": self.source_policy,
            "boundary_sensitive": self.boundary_sensitive,
            "review_required": self.review_required,
            "high_risk": self.high_risk,
            "notes": list(self.notes),
        }
