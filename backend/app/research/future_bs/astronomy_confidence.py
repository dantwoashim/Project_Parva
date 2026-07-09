"""Separate astronomical precision from civil/source authority confidence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

AstronomyStatus = Literal["jpl_verified", "fallback_computed", "unavailable"]
CivilAuthorityStatus = Literal["official_source", "published_source", "computed_not_official"]


@dataclass(frozen=True)
class AstronomyConfidence:
    astronomy_status: AstronomyStatus
    civil_authority_status: CivilAuthorityStatus
    boundary_risk: Literal["low", "medium", "high", "unknown"]
    claim_boundary: str = "astronomy_evidence_not_civil_authority"
    review_required: bool = True

    def payload(self) -> dict[str, object]:
        return {
            "astronomy_status": self.astronomy_status,
            "civil_authority_status": self.civil_authority_status,
            "boundary_risk": self.boundary_risk,
            "claim_boundary": self.claim_boundary,
            "review_required": self.review_required,
            "not_authority": (
                "Astronomical computation is evidence. Official bodies and "
                "published sources remain authoritative for civil decisions."
            ),
        }


def classify_astronomy_confidence(
    *,
    jpl_available: bool,
    has_official_source: bool = False,
    has_published_source: bool = False,
    minutes_to_boundary: float | None = None,
) -> AstronomyConfidence:
    if has_official_source:
        civil = "official_source"
        review = False
    elif has_published_source:
        civil = "published_source"
        review = True
    else:
        civil = "computed_not_official"
        review = True

    if minutes_to_boundary is None:
        risk = "unknown"
    elif abs(minutes_to_boundary) <= 30:
        risk = "high"
    elif abs(minutes_to_boundary) <= 180:
        risk = "medium"
    else:
        risk = "low"

    return AstronomyConfidence(
        astronomy_status="jpl_verified" if jpl_available else "fallback_computed",
        civil_authority_status=civil,
        boundary_risk=risk,
        review_required=review or risk in {"high", "medium", "unknown"},
    )
