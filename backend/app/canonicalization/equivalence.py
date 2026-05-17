"""Canonicalization equivalence helpers."""

from __future__ import annotations

from app.canonicalization.normalize import canonicalize_query, identity_hash


def equivalent(left: dict, right: dict) -> bool:
    return identity_hash(left) == identity_hash(right)


def canonical_pair(left: dict, right: dict) -> tuple[dict, dict]:
    return canonicalize_query(left), canonicalize_query(right)
