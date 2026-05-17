"""In-memory witness registry for local verification tests."""

from __future__ import annotations

from app.witnesses.schema import Witness


class WitnessRegistry:
    def __init__(self) -> None:
        self._witnesses: dict[str, Witness] = {}

    def add(self, witness: Witness) -> str:
        self._witnesses[witness.witness_id] = witness
        return witness.witness_id

    def get(self, witness_id: str) -> Witness:
        return self._witnesses[witness_id]
