"""Witness content hashing."""

from __future__ import annotations

from typing import Any

from app.sources.hashing import canonical_json_hash


def witness_hash(payload: dict[str, Any]) -> str:
    return f"parva:wit:v1:sha256:{canonical_json_hash(payload)}"
