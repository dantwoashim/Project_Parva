"""Conformance badge schema."""

from __future__ import annotations

from app.sources.hashing import canonical_json_hash


def generate_badge(report: dict) -> dict:
    badge = {
        "kind": "parva_conformance_badge",
        "capsule_version": "1.0.0",
        "test_pack": report.get("capsule_id", "unknown"),
        "status": "passing_reference_report",
        "expiration": "review_required_before_public_marketing",
        "claim_boundary": "badge_is_self_attested_not_certification",
    }
    badge["witness_hash"] = f"sha256:{canonical_json_hash(report)}"
    return badge
