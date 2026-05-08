"""Source reliability weights used by weak-label and latent-truth models."""

from __future__ import annotations

from typing import Any

PUBLICATION_STATUS = "computed_prediction_not_official"

SOURCE_RELIABILITY = {
    "official_verified": 0.98,
    "printed_verified": 0.9,
    "public_daily_witness": 0.75,
    "publisher_reference": 0.58,
    "software_table_reference": 0.38,
    "third_party_reference": 0.25,
    "needs_review": 0.05,
    "excluded": 0.0,
}


def reliability_for_source_type(source_type: str) -> float:
    return SOURCE_RELIABILITY.get(source_type, 0.05)


def reliability_payload() -> dict[str, Any]:
    return {
        "publication_status": PUBLICATION_STATUS,
        "source_reliability": SOURCE_RELIABILITY,
        "official_claim_policy": "Tier 5/6 weights are never allowed to create official_strict claim-readiness.",
    }
