from __future__ import annotations

from scripts.validate_external_temporal_rules import (
    validate_external_temporal_rules,
    validate_registry,
)


def test_external_temporal_rules_registry_passes() -> None:
    assert validate_external_temporal_rules() == []


def test_registry_rejects_duplicate_rule_ids() -> None:
    payload = {
        "claim_boundary": "institution_rule_registry_not_authority",
        "source_tiers": ["official", "semi_official", "institutional", "published", "research", "unknown"],
        "rules": [
            {
                "rule_id": "duplicate_rule",
                "name": "A",
                "authority_type": "research",
                "source_tier": "research",
                "applies_to": ["working_days"],
                "evidence_required": ["policy"],
                "public_safe": True,
                "review_required_when": ["final use"],
                "conflict_resolution": "review",
                "examples": ["example"],
            },
            {
                "rule_id": "duplicate_rule",
                "name": "B",
                "authority_type": "research",
                "source_tier": "research",
                "applies_to": ["working_days"],
                "evidence_required": ["policy"],
                "public_safe": True,
                "review_required_when": ["final use"],
                "conflict_resolution": "review",
                "examples": ["example"],
            },
        ],
    }

    assert any("duplicate" in issue for issue in validate_registry(payload))


def test_registry_rejects_final_authority_wording() -> None:
    payload = {
        "claim_boundary": "institution_rule_registry_not_authority",
        "source_tiers": ["official", "semi_official", "institutional", "published", "research", "unknown"],
        "rules": [
            {
                "rule_id": "bad_rule",
                "name": "Bad",
                "authority_type": "research",
                "source_tier": "research",
                "applies_to": ["bank_holidays"],
                "evidence_required": ["policy"],
                "public_safe": True,
                "review_required_when": ["final use"],
                "conflict_resolution": "review",
                "examples": ["This is banking authority."],
            }
        ],
    }

    assert any("banking authority" in issue for issue in validate_registry(payload))
