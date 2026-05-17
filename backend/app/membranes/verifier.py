"""Local membrane verifier."""

from __future__ import annotations

from app.canonicalization.normalize import identity_hash
from app.sources.hashing import canonical_json_hash
from app.witnesses.hashing import witness_hash


def verify_membrane(membrane: dict) -> tuple[bool, str]:
    if identity_hash(membrane["canonical_query"]) != membrane["identity_hash"]:
        return False, "identity_hash_mismatch"
    result_hash = f"sha256:{canonical_json_hash(membrane['result'])}"
    witness = dict(membrane["witness"])
    if witness.get("output_hash") != result_hash:
        return False, "witness_output_hash_mismatch"
    witness_id = witness.pop("witness_id", None)
    if witness_hash(witness) != witness_id or witness_id != membrane["witness_hash"]:
        return False, "witness_hash_mismatch"
    return True, "verified"
