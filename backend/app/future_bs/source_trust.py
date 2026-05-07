"""Source trust taxonomy for future BS corpus and claims."""

from __future__ import annotations

from typing import Any

TRUST_LEVELS: dict[str, dict[str, Any]] = {
    "official_verified": {
        "level": 1,
        "claim_use": "final_claim_allowed",
        "description": "NPNS, government, or official published calendar evidence.",
    },
    "printed_verified": {
        "level": 2,
        "claim_use": "final_claim_allowed_after_review",
        "description": "Scanned printed Patro with identifiable publisher and human review.",
    },
    "physical_patro_verified": {
        "level": 2,
        "claim_use": "final_claim_allowed_after_review",
        "description": "Reviewed physical Patro evidence retained in the source archive.",
    },
    "institutional_reference": {
        "level": 3,
        "claim_use": "training_or_comparison_only",
        "description": "Bank, insurer, ERP, accounting, or internal calendar reference.",
    },
    "publisher_consensus": {
        "level": 3,
        "claim_use": "training_or_comparison_only",
        "description": "Multiple independent publishers or apps agree.",
    },
    "third_party_reference": {
        "level": 4,
        "claim_use": "comparison_only",
        "description": "Single app, site, scraped, or legacy table reference.",
    },
    "scraped_reference": {
        "level": 4,
        "claim_use": "comparison_only",
        "description": "Scraped reference row that needs source review.",
    },
    "needs_review": {
        "level": 5,
        "claim_use": "excluded",
        "description": "Unverified, conflicting, or incomplete evidence.",
    },
    "excluded": {
        "level": 6,
        "claim_use": "excluded",
        "description": "Known bad, inconsistent, or unusable evidence.",
    },
}


def source_trust_payload(source_type: str) -> dict[str, Any]:
    payload = TRUST_LEVELS.get(
        source_type,
        {
            "level": 6,
            "claim_use": "excluded",
            "description": "Unknown source type.",
        },
    )
    return {"source_type": source_type, **payload}
