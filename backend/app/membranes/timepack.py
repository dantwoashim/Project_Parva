"""Portable Timepack v1 wrapper and verifier."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.membranes.proofpack import proof_pack, verify_proof_pack
from app.sources.hashing import canonical_json_hash


def build_timepack(membrane: dict, level: str) -> dict:
    pack = proof_pack(membrane, level)
    return {
        "kind": "parva_timepack",
        "timepack_version": "v1",
        "level": level,
        "artifact_type": membrane["canonical_query"]["operation"],
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "payload": pack,
        "proof_packs": [pack],
        "aggregate_witness_hash": f"sha256:{canonical_json_hash([pack.get('witness_hash') or membrane['witness_hash']])}",
        "boundary_summary": {
            "not_authority": True,
            "review_required": membrane.get("boundary", {}).get("review_state") == "required",
            "claim_boundary": membrane.get("boundary", {}).get("claim_boundary"),
        },
        "result_summary": membrane.get("result"),
        "replay_instructions": "Run `parva verify-timepack <path>` from a checkout with committed proof fixtures.",
    }


def verify_timepack(timepack: dict[str, Any]) -> tuple[bool, str]:
    if timepack.get("kind") != "parva_timepack" or timepack.get("timepack_version") != "v1":
        return False, "timepack_schema_invalid"
    packs = timepack.get("proof_packs")
    if not isinstance(packs, list) or not packs:
        return False, "timepack_proof_packs_missing"
    child_hashes: list[str] = []
    for pack in packs:
        if not isinstance(pack, dict):
            return False, "timepack_child_invalid"
        ok, reason = verify_proof_pack(pack)
        if not ok:
            return False, f"child_{reason}"
        child_hash = pack.get("witness_hash") or (pack.get("membrane") or {}).get("witness_hash")
        if not isinstance(child_hash, str):
            return False, "timepack_child_witness_hash_missing"
        child_hashes.append(child_hash)
    if timepack.get("aggregate_witness_hash") != f"sha256:{canonical_json_hash(child_hashes)}":
        return False, "timepack_aggregate_hash_mismatch"
    boundary = timepack.get("boundary_summary")
    if not isinstance(boundary, dict) or not boundary.get("not_authority"):
        return False, "timepack_boundary_summary_missing"
    return True, "verified"
