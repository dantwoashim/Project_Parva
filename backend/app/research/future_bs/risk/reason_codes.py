"""Reason codes used by the public-safe future-BS risk alpha."""

from __future__ import annotations

from enum import Enum


class RiskReasonCode(str, Enum):
    LOW_RISK_CURRENT_CHECKS = "low_risk_current_checks"
    BOUNDARY_SENSITIVE = "boundary_sensitive"
    REVIEW_RECOMMENDED = "review_recommended"
    SOURCE_CONFLICT = "source_conflict"
    INSUFFICIENT_CONFIDENCE = "insufficient_confidence"
    INVALID_MONTH_LENGTH = "invalid_month_length"
    INVALID_YEAR_TOTAL = "invalid_year_total"
    NON_CLAIMABLE = "non_claimable"
    SYNTHETIC_EXAMPLE = "synthetic_example"


REASON_CODE_DESCRIPTIONS: dict[RiskReasonCode, str] = {
    RiskReasonCode.LOW_RISK_CURRENT_CHECKS: "The public risk checks found no immediate review trigger.",
    RiskReasonCode.BOUNDARY_SENSITIVE: "The month assumption sits on a boundary-sensitive length.",
    RiskReasonCode.REVIEW_RECOMMENDED: "A human or source-policy review is recommended before operational use.",
    RiskReasonCode.SOURCE_CONFLICT: "Available source signals conflict or are not independently resolved.",
    RiskReasonCode.INSUFFICIENT_CONFIDENCE: "The evidence does not support a stronger public posture.",
    RiskReasonCode.INVALID_MONTH_LENGTH: "The supplied month length is outside the supported BS review envelope.",
    RiskReasonCode.INVALID_YEAR_TOTAL: "A complete year total is outside the normal 365 or 366 day envelope.",
    RiskReasonCode.NON_CLAIMABLE: "The case is not safe to claim without stronger source authority.",
    RiskReasonCode.SYNTHETIC_EXAMPLE: "The row is synthetic and exists only to demonstrate shape.",
}


def reason_code_values() -> list[str]:
    """Return stable serialized reason code values."""

    return [reason.value for reason in RiskReasonCode]
