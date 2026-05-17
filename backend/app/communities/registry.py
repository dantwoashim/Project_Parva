"""Community branch registry."""

from __future__ import annotations

COMMUNITIES = {
    "canonical": {"authority_scope": "national_reference", "can_override_civil": False},
    "official_only": {"authority_scope": "official_publications", "can_override_civil": False},
    "community_sample": {"authority_scope": "community_specific", "can_override_civil": False},
}


def get_community_policy(policy_id: str) -> dict:
    return COMMUNITIES[policy_id]
