"""Witness freshness resolution."""

from __future__ import annotations


def resolve_freshness(witness_hash: str, current_hashes: set[str], superseded_by: str | None = None) -> dict:
    if witness_hash in current_hashes:
        return {"status": "current", "witness_hash": witness_hash}
    if superseded_by:
        return {"status": "valid_superseded", "witness_hash": witness_hash, "superseded_by": superseded_by}
    return {"status": "contradicted_or_unknown", "witness_hash": witness_hash}
