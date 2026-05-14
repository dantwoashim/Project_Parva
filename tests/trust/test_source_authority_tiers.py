from __future__ import annotations

import json
from pathlib import Path

from app.core.source_authority import (
    PUBLIC_RELEASE_SOURCE_TIERS,
    SOURCE_AUTHORITY_TIER_POLICIES,
    SOURCE_AUTHORITY_TIERS,
)
from app.services.trust_infrastructure_service import ALLOWED_SOURCE_TIERS

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _enum_at(path: str, *keys: str) -> list[str]:
    payload = json.loads((PROJECT_ROOT / path).read_text(encoding="utf-8"))
    node = payload
    for key in keys:
        node = node[key]
    return list(node["enum"])


def test_canonical_source_ref_schema_matches_runtime_tiers() -> None:
    schema_tiers = _enum_at("schemas/source-ref.schema.json", "properties", "source_tier")

    assert schema_tiers == list(SOURCE_AUTHORITY_TIERS)


def test_protocol_source_record_schema_matches_runtime_tiers() -> None:
    schema_tiers = _enum_at(
        "schemas/parva-protocol/source-record.schema.json",
        "properties",
        "source_tier",
    )

    assert schema_tiers == list(SOURCE_AUTHORITY_TIERS)


def test_public_release_source_registry_schema_uses_public_subset() -> None:
    schema_tiers = _enum_at(
        "schemas/source-registry.schema.json",
        "properties",
        "sources",
        "items",
        "properties",
        "source_tier",
    )

    assert schema_tiers == list(PUBLIC_RELEASE_SOURCE_TIERS)
    assert set(ALLOWED_SOURCE_TIERS) == set(PUBLIC_RELEASE_SOURCE_TIERS)
    assert "research_private" not in schema_tiers


def test_all_source_tier_policy_rows_match_canonical_tiers() -> None:
    assert list(SOURCE_AUTHORITY_TIER_POLICIES) == list(SOURCE_AUTHORITY_TIERS)
    for tier, policy in SOURCE_AUTHORITY_TIER_POLICIES.items():
        assert isinstance(policy["public_output"], bool), tier
        assert isinstance(policy["official_looking_claims"], bool), tier
        assert isinstance(policy["requires_human_review"], bool), tier
        assert isinstance(policy["public_offline_bundle"], bool), tier
        assert isinstance(policy["conflict_rank"], int), tier


def test_webhook_source_tier_schema_matches_runtime_tiers() -> None:
    schema_tiers = _enum_at("schemas/webhooks/calendar_events.schema.json", "properties", "source_tier")

    assert schema_tiers == list(SOURCE_AUTHORITY_TIERS)


def test_public_future_bs_source_tier_schema_matches_runtime_tiers() -> None:
    payload = json.loads(
        (PROJECT_ROOT / "data/future_bs/public/source_tier_schema.json").read_text(
            encoding="utf-8"
        )
    )
    schema_tiers = [row["tier"] for row in payload["tiers"]]

    assert schema_tiers == list(SOURCE_AUTHORITY_TIERS)
