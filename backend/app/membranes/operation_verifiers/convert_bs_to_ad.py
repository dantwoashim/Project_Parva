"""Replay verifier for convert_bs_to_ad membranes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.calendar.bikram_sambat import bs_to_gregorian
from app.membranes.source_resolution import resolve_convert_bs_to_ad_source
from app.sources.hashing import canonical_json_hash
from app.trust.taint import AuthorityTaint

PROJECT_ROOT = Path(__file__).resolve().parents[4]
SOURCE_SNAPSHOT_PATH = PROJECT_ROOT / "data" / "sources" / "source_snapshot.json"


def _current_source_snapshot_hash() -> str:
    try:
        payload = json.loads(SOURCE_SNAPSHOT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return "sha256:source_snapshot_unavailable"
    return str(payload.get("snapshot_hash") or "sha256:source_snapshot_missing_hash")


def _input_parts(membrane: dict[str, Any]) -> tuple[int, int, int]:
    payload = membrane.get("canonical_query", {}).get("input", {})
    return int(payload["year"]), int(payload["month"]), int(payload["day"])


def verify_convert_bs_to_ad_replay(membrane: dict[str, Any]) -> tuple[bool, str]:
    try:
        year, month, day = _input_parts(membrane)
    except (KeyError, TypeError, ValueError):
        return False, "canonical_query_input_invalid"

    expected_result = {"ad_date": bs_to_gregorian(year, month, day).isoformat()}
    if membrane.get("result") != expected_result:
        return False, "replayed_result_mismatch"

    expected_source_hash = _current_source_snapshot_hash()
    if membrane.get("source_snapshot_hash") != expected_source_hash:
        return False, "source_snapshot_hash_mismatch"

    proof_pack = membrane.get("proof_pack")
    if not isinstance(proof_pack, dict):
        return False, "proof_pack_missing"
    source_artifacts = proof_pack.get("source_artifacts")
    if not isinstance(source_artifacts, dict):
        return False, "proof_pack_source_artifacts_missing"
    if source_artifacts.get("source_snapshot_hash") != expected_source_hash:
        return False, "proof_pack_source_snapshot_mismatch"

    steps = proof_pack.get("steps")
    if not isinstance(steps, list) or len(steps) < 2:
        return False, "proof_pack_steps_missing"
    conversion_steps = [step for step in steps if isinstance(step, dict) and step.get("operation") == "convert_bs_to_ad"]
    if not conversion_steps:
        return False, "proof_pack_replay_step_missing"
    if conversion_steps[-1].get("output_hash") != f"sha256:{canonical_json_hash(expected_result)}":
        return False, "proof_pack_result_hash_mismatch"

    resolution = resolve_convert_bs_to_ad_source(year, month, day)
    membrane_dockets = tuple(membrane.get("source_docket_ids") or ())
    if membrane_dockets != resolution.source_docket_ids:
        return False, "source_docket_resolution_mismatch"

    boundary = membrane.get("boundary")
    if not isinstance(boundary, dict):
        return False, "boundary_vector_missing"
    if boundary.get("authority") != resolution.authority.value:
        return False, "boundary_authority_mismatch"
    if boundary.get("review_state") == "not_required" and resolution.review_required:
        return False, "boundary_review_state_mismatch"

    field_provenance = membrane.get("field_provenance")
    if not isinstance(field_provenance, dict) or "ad_date" not in field_provenance:
        return False, "field_provenance_missing"
    ad_date_provenance = field_provenance["ad_date"]
    if ad_date_provenance.get("authority") != resolution.authority.value:
        return False, "field_authority_mismatch"
    if ad_date_provenance.get("source_docket_id") not in (resolution.source_docket_ids[0] if resolution.source_docket_ids else None, None):
        return False, "field_source_docket_mismatch"
    if resolution.review_required and "review_required" not in set(ad_date_provenance.get("flags") or []):
        return False, "field_review_required_missing"

    if (
        not resolution.eligible_official
        and ad_date_provenance.get("authority")
        in {AuthorityTaint.STRUCTURED_OFFICIAL.value, AuthorityTaint.ARCHIVED_OFFICIAL.value}
    ):
        return False, "source_authority_overclaim"

    return True, "replayed"


__all__ = ["verify_convert_bs_to_ad_replay"]
