"""Replay verifier for proof-carrying Panchanga summary membranes."""

from __future__ import annotations

from typing import Any

from app.panchanga.ephemeris_provider import FixtureEphemerisProvider
from app.panchanga.proof import build_panchanga_summary_capsule
from app.sources.hashing import canonical_json_hash


def _fixture_hash_matches(membrane: dict[str, Any]) -> bool:
    metadata = membrane.get("ephemeris_metadata")
    if not isinstance(metadata, dict) or metadata.get("provider_kind") != "pinned_fixture":
        return True
    fixture_id = metadata.get("fixture_id")
    if not isinstance(fixture_id, str):
        return False
    try:
        expected = FixtureEphemerisProvider(fixture_id=fixture_id).metadata()
    except (OSError, ValueError, KeyError):
        return False
    return metadata.get("kernel_hash") == expected.get("kernel_hash")


def verify_panchanga_summary_replay(membrane: dict[str, Any]) -> tuple[bool, str]:
    try:
        query = membrane["canonical_query"]
        input_payload = query["input"]
        context = query["context"]
        target_date = __import__("datetime").date.fromisoformat(str(input_payload["date"]))
        latitude = float(context["latitude"])
        longitude = float(context["longitude"])
        timezone_name = str(context["timezone"])
        provider_id = str(context["ephemeris_provider"])
        fixture_id = context.get("ephemeris_fixture_id")
        fixture_text = str(fixture_id) if fixture_id not in (None, "none", "") else None
        ayanamsa = str(context["ayanamsa"])
        sunrise_rule = str(context["sunrise_rule"])
    except (KeyError, TypeError, ValueError):
        return False, "canonical_query_input_invalid"

    if not _fixture_hash_matches(membrane):
        return False, "ephemeris_fixture_hash_mismatch"

    expected = build_panchanga_summary_capsule(
        target_date,
        latitude=latitude,
        longitude=longitude,
        timezone_name=timezone_name,
        provider_id=provider_id,
        fixture_id=fixture_text,
        ayanamsa=ayanamsa,
        sunrise_rule=sunrise_rule,
    )
    if membrane.get("result") != expected["result"]:
        return False, "replayed_result_mismatch"
    if membrane.get("ephemeris_metadata") != expected["ephemeris_metadata"]:
        return False, "ephemeris_metadata_mismatch"
    if membrane.get("method_docket_refs") != expected["method_docket_refs"]:
        return False, "method_docket_refs_mismatch"
    proof_pack = membrane.get("proof_pack")
    if not isinstance(proof_pack, dict):
        return False, "proof_pack_missing"
    steps = proof_pack.get("steps")
    if not isinstance(steps, list) or len(steps) < 2:
        return False, "proof_pack_steps_missing"
    if steps[-1].get("output_hash") != f"sha256:{canonical_json_hash(expected['result'])}":
        return False, "proof_pack_result_hash_mismatch"
    field_provenance = membrane.get("field_provenance")
    if not isinstance(field_provenance, dict):
        return False, "field_provenance_missing"
    for field in expected["result"]:
        provenance = field_provenance.get(field)
        if not isinstance(provenance, dict) or not provenance.get("authority"):
            return False, "field_provenance_missing"
    boundary = membrane.get("boundary")
    if not isinstance(boundary, dict):
        return False, "boundary_vector_missing"
    if not boundary.get("not_panchanga_authority") or not boundary.get("not_ritual_final_authority"):
        return False, "panchanga_authority_boundary_missing"
    return True, "replayed"


__all__ = ["verify_panchanga_summary_replay"]
