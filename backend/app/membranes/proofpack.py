"""Standalone proof pack artifacts."""

from __future__ import annotations

from typing import Any

from app.membranes.verifier import verify_membrane


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
            "kind": "parva_proofpack",
            "proofpack_version": "v1",
            "level": "audit",
            "membrane": membrane,
            "source_docket_ids": membrane["source_docket_ids"],
            "identity_hash": membrane["identity_hash"],
            "witness_hash": membrane["witness_hash"],
            "boundary": membrane["boundary"],
        }
    if level == "replay":
        return {
            "kind": "parva_proofpack",
            "proofpack_version": "v1",
            "level": "replay",
            "membrane": membrane,
            "offline_verifier": "parva_membrane_replay_v1",
            "identity_hash": membrane["identity_hash"],
            "witness_hash": membrane["witness_hash"],
            "boundary": membrane["boundary"],
        }
    raise ValueError("proof pack level must be compact, audit, or replay")


def verify_proof_pack(pack: dict[str, Any]) -> tuple[bool, str]:
    level = str(pack.get("level") or "")
    if level == "compact":
        required = {"identity_hash", "witness_hash", "boundary"}
        if not required.issubset(pack):
            return False, "compact_proofpack_missing_fields"
        if not isinstance(pack.get("boundary"), dict) or not pack["boundary"].get("claim_boundary"):
            return False, "compact_proofpack_boundary_missing"
        return True, "verified_compact_proofpack"
    membrane = pack.get("membrane")
    if not isinstance(membrane, dict):
        return False, "proofpack_membrane_missing"
    ok, reason = verify_membrane(membrane)
    if not ok:
        return False, reason
    if pack.get("identity_hash") and pack.get("identity_hash") != membrane.get("identity_hash"):
        return False, "proofpack_identity_hash_mismatch"
    if pack.get("witness_hash") and pack.get("witness_hash") != membrane.get("witness_hash"):
        return False, "proofpack_witness_hash_mismatch"
    return True, "verified"
