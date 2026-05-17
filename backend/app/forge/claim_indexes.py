"""Deterministic claim index roots for public verification bundles."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.sources.hashing import canonical_json_hash


@dataclass(frozen=True)
class ClaimIndexEntry:
    claim_id: str
    identity_hash: str
    witness_hash: str
    source_snapshot_hash: str
    boundary: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "identity_hash": self.identity_hash,
            "witness_hash": self.witness_hash,
            "source_snapshot_hash": self.source_snapshot_hash,
            "boundary": self.boundary,
        }


def entry_hash(entry: ClaimIndexEntry) -> str:
    return f"sha256:{canonical_json_hash(entry.as_dict())}"


def build_claim_index(entries: list[ClaimIndexEntry]) -> dict[str, Any]:
    ordered = sorted(entries, key=lambda item: item.claim_id)
    leaf_hashes = [entry_hash(entry) for entry in ordered]
    return {
        "kind": "parva_claim_index",
        "version": "1.0.0",
        "entries": [entry.as_dict() for entry in ordered],
        "leaf_hashes": leaf_hashes,
        "root_hash": f"sha256:{canonical_json_hash(leaf_hashes)}",
    }
