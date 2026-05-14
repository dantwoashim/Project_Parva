"""Canonical source authority tiers for public trust artifacts."""

from __future__ import annotations

SOURCE_AUTHORITY_TIERS: tuple[str, ...] = (
    "official",
    "semi_official",
    "printed_verified",
    "public_witness",
    "publisher_reference",
    "software_table_reference",
    "third_party",
    "calculated",
    "fixture",
    "research_private",
    "unknown",
)

SOURCE_AUTHORITY_TIER_POLICIES: dict[str, dict[str, object]] = {
    "official": {
        "public_output": True,
        "official_looking_claims": True,
        "requires_human_review": True,
        "public_offline_bundle": True,
        "conflict_rank": 100,
    },
    "semi_official": {
        "public_output": True,
        "official_looking_claims": False,
        "requires_human_review": True,
        "public_offline_bundle": True,
        "conflict_rank": 90,
    },
    "printed_verified": {
        "public_output": True,
        "official_looking_claims": False,
        "requires_human_review": True,
        "public_offline_bundle": True,
        "conflict_rank": 80,
    },
    "public_witness": {
        "public_output": True,
        "official_looking_claims": False,
        "requires_human_review": True,
        "public_offline_bundle": True,
        "conflict_rank": 70,
    },
    "publisher_reference": {
        "public_output": True,
        "official_looking_claims": False,
        "requires_human_review": False,
        "public_offline_bundle": True,
        "conflict_rank": 60,
    },
    "software_table_reference": {
        "public_output": True,
        "official_looking_claims": False,
        "requires_human_review": False,
        "public_offline_bundle": True,
        "conflict_rank": 50,
    },
    "third_party": {
        "public_output": True,
        "official_looking_claims": False,
        "requires_human_review": True,
        "public_offline_bundle": True,
        "conflict_rank": 40,
    },
    "calculated": {
        "public_output": True,
        "official_looking_claims": False,
        "requires_human_review": False,
        "public_offline_bundle": True,
        "conflict_rank": 30,
    },
    "fixture": {
        "public_output": False,
        "official_looking_claims": False,
        "requires_human_review": False,
        "public_offline_bundle": False,
        "conflict_rank": 10,
    },
    "research_private": {
        "public_output": False,
        "official_looking_claims": False,
        "requires_human_review": True,
        "public_offline_bundle": False,
        "conflict_rank": 20,
    },
    "unknown": {
        "public_output": False,
        "official_looking_claims": False,
        "requires_human_review": True,
        "public_offline_bundle": False,
        "conflict_rank": 0,
    },
}

PUBLIC_RELEASE_SOURCE_TIERS: tuple[str, ...] = tuple(
    tier for tier in SOURCE_AUTHORITY_TIERS if tier != "research_private"
)

PRIVATE_ONLY_SOURCE_TIERS: frozenset[str] = frozenset({"research_private"})

SOURCE_TIER_ALIASES: dict[str, str] = {
    "public_corpus": "software_table_reference",
    "publisher": "publisher_reference",
    "research": "research_private",
    "private": "research_private",
    "third_party_reference": "third_party",
    "official_verified": "official",
    "public_daily_witness": "public_witness",
}


def normalize_source_tier(value: str | None) -> str:
    """Return the canonical tier for legacy source-tier labels."""
    normalized = str(value or "unknown").strip().lower()
    return SOURCE_TIER_ALIASES.get(
        normalized,
        normalized if normalized in SOURCE_AUTHORITY_TIERS else "unknown",
    )
