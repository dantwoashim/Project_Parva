"""Causal bitplanes for compact temporal truth vectors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.sources.hashing import canonical_json_hash


@dataclass(frozen=True)
class CausalBitplane:
    name: str
    bits: tuple[bool, ...]
    witness_refs: tuple[str, ...]
    cause_stamps: tuple[dict[str, Any], ...]

    def __post_init__(self) -> None:
        if len(self.bits) != len(self.cause_stamps):
            raise ValueError("cause_stamps length must match bits length")

    @property
    def hash(self) -> str:
        return f"sha256:{canonical_json_hash(self.as_dict(include_hash=False))}"

    def as_dict(self, *, include_hash: bool = True) -> dict[str, Any]:
        payload = {
            "kind": "causal_bitplane",
            "name": self.name,
            "bits": list(self.bits),
            "witness_refs": list(self.witness_refs),
            "cause_stamps": list(self.cause_stamps),
        }
        if include_hash:
            payload["hash"] = self.hash
        return payload
