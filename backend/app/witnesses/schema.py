"""Witness schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.witnesses.hashing import witness_hash


@dataclass(frozen=True)
class Witness:
    operation: str
    input_hash: str
    output_hash: str
    verifier: str
    verifier_version: str
    method_parameters: dict[str, Any]
    source_refs: tuple[str, ...]

    @property
    def witness_id(self) -> str:
        return witness_hash(self.as_dict(include_id=False))

    def as_dict(self, *, include_id: bool = True) -> dict[str, Any]:
        payload = {
            "operation": self.operation,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "verifier": self.verifier,
            "verifier_version": self.verifier_version,
            "method_parameters": self.method_parameters,
            "source_refs": list(self.source_refs),
        }
        if include_id:
            payload["witness_id"] = self.witness_id
        return payload
