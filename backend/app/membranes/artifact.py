"""Membrane artifact hashing."""

from __future__ import annotations

from app.sources.hashing import canonical_json_hash


def artifact_hash(membrane: dict) -> str:
    payload = {key: value for key, value in membrane.items() if key != "artifact_hash"}
    return f"parva:art:v1:sha256:{canonical_json_hash(payload)}"
