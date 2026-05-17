"""Shared replay checks for civil temporal membranes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from app.sources.hashing import canonical_json_hash
from app.trust.taint import AuthorityTaint

PROJECT_ROOT = Path(__file__).resolve().parents[4]
SOURCE_SNAPSHOT_PATH = PROJECT_ROOT / "data" / "sources" / "source_snapshot.json"


def current_source_snapshot_hash() -> str:
    try:
        payload = json.loads(SOURCE_SNAPSHOT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return "sha256:source_snapshot_unavailable"
    return str(payload.get("snapshot_hash") or "sha256:source_snapshot_missing_hash")


def verify_common_replay(
    membrane: dict[str, Any],
    *,
    operation: str,
    replay_step: str,
    expected_result: dict[str, Any],
    expected_source_resolution: Callable[[], Any],
) -> tuple[bool, str]:
    if membrane.get("result") != expected_result:
        return False, "replayed_result_mismatch"

    expected_source_hash = current_source_snapshot_hash()
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
    replay_steps = [step for step in steps if isinstance(step, dict) and step.get("operation") == replay_step]
    if not replay_steps:
        return False, "proof_pack_replay_step_missing"
    if replay_steps[-1].get("output_hash") != f"sha256:{canonical_json_hash(expected_result)}":
        return False, "proof_pack_result_hash_mismatch"

    resolution = expected_source_resolution()
    membrane_dockets = tuple(membrane.get("source_docket_ids") or ())
    if membrane_dockets != resolution.source_docket_ids:
        return False, "source_docket_resolution_mismatch"

    boundary = membrane.get("boundary")
    if not isinstance(boundary, dict):
        return False, "boundary_vector_missing"
    if boundary.get("authority") != resolution.authority.value and operation not in {
        "holiday",
        "working_day",
        "fiscal_year",
        "bs_months",
    }:
        return False, "boundary_authority_mismatch"
    if boundary.get("review_state") == "not_required" and resolution.review_required:
        return False, "boundary_review_state_mismatch"
    if not boundary.get("claim_boundary"):
        return False, "boundary_claim_missing"

    policy_trace = membrane.get("policy_trace")
    if not isinstance(policy_trace, dict) or policy_trace.get("operation") != operation:
        return False, "policy_trace_missing"

    field_provenance = membrane.get("field_provenance")
    if not isinstance(field_provenance, dict):
        return False, "field_provenance_missing"
    missing = sorted(field for field in expected_result if field not in field_provenance)
    if missing:
        return False, "field_provenance_missing"
    for provenance in field_provenance.values():
        if not isinstance(provenance, dict):
            return False, "field_provenance_invalid"
        if not provenance.get("authority"):
            return False, "field_authority_missing"
        if resolution.review_required and "review_required" not in set(provenance.get("flags") or []):
            return False, "field_review_required_missing"
        if (
            not resolution.eligible_official
            and provenance.get("authority")
            in {AuthorityTaint.STRUCTURED_OFFICIAL.value, AuthorityTaint.ARCHIVED_OFFICIAL.value}
        ):
            return False, "source_authority_overclaim"

    return True, "replayed"
