"""Bitplane attestation objects."""

from __future__ import annotations

from dataclasses import dataclass

from app.bitplanes.causal import CausalBitplane
from app.sources.hashing import canonical_json_hash


@dataclass(frozen=True)
class BitplaneAttestation:
    plane_hash: str
    manifest_hash: str

    @property
    def attestation_hash(self) -> str:
        return f"sha256:{canonical_json_hash({'plane_hash': self.plane_hash, 'manifest_hash': self.manifest_hash})}"


def attest_bitplane(plane: CausalBitplane, manifest_hash: str) -> BitplaneAttestation:
    return BitplaneAttestation(plane_hash=plane.hash, manifest_hash=manifest_hash)
