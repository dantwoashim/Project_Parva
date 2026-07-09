"""Public-safe risk label definitions for future-BS review posture."""

from __future__ import annotations

from enum import Enum

PUBLICATION_STATUS = "computed_prediction_not_official"


class RiskLabel(str, Enum):
    """Risk labels exposed by the public future-BS risk alpha."""

    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


RISK_LABEL_DEFINITIONS: dict[RiskLabel, str] = {
    RiskLabel.GREEN: (
        "Low risk under current evidence and checks, still not official publication."
    ),
    RiskLabel.YELLOW: (
        "Review recommended. Boundary-sensitive, source-conflicted, or insufficient confidence."
    ),
    RiskLabel.RED: "Unsafe, invalid, source-conflicted, or non-claimable.",
}


def risk_label_values() -> list[str]:
    """Return stable serialized risk label values."""

    return [label.value for label in RiskLabel]
