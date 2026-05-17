"""Proof pack levels."""

from __future__ import annotations


def proof_pack(membrane: dict, level: str) -> dict:
    if level == "compact":
        return {
            "level": "compact",
            "identity_hash": membrane["identity_hash"],
            "witness_hash": membrane["witness_hash"],
            "boundary": membrane["boundary"],
        }
    if level == "audit":
        return {
            "level": "audit",
            "membrane": membrane,
            "source_docket_ids": membrane["source_docket_ids"],
        }
    if level == "replay":
        return {
            "level": "replay",
            "membrane": membrane,
            "offline_verifier": "parva_membrane_replay_v1",
        }
    raise ValueError("proof pack level must be compact, audit, or replay")
