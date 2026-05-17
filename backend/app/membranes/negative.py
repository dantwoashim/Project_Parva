"""Negative membranes for supported absence proofs."""

from __future__ import annotations


def negative_membrane(claim: str, reason: str, witness_refs: list[str]) -> dict:
    return {
        "kind": "parva_membrane",
        "membrane_kind": "negative",
        "claim": claim,
        "reason": reason,
        "witness_refs": witness_refs,
        "review_required": False,
        "claim_boundary": "absence_proof_within_supported_source_universe",
    }
