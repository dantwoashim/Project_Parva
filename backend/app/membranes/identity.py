"""Identity hashing for canonical queries."""

from __future__ import annotations

from app.canonicalization.normalize import identity_hash


def membrane_identity_hash(canonical_query: dict) -> str:
    return identity_hash(canonical_query)
