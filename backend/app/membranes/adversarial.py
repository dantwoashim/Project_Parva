"""Adversarial membrane checks for tamper and overclaim probes."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.membranes.verifier import verify_membrane


def tamper_result_probe(membrane: dict[str, Any], field: str, value: Any) -> dict[str, Any]:
    tampered = deepcopy(membrane)
    tampered.setdefault("result", {})[field] = value
    verified, reason = verify_membrane(tampered)
    return {
        "kind": "adversarial_probe",
        "probe": "tamper_result",
        "field": field,
        "verified": verified,
        "reason": reason,
        "expected": "verification_failure",
    }


def authority_overclaim_probe(membrane: dict[str, Any], claimed_authority: str) -> dict[str, Any]:
    boundary = membrane.get("boundary") or {}
    blocked = set(boundary.get("blocked_use_cases") or [])
    unsafe = claimed_authority in blocked or claimed_authority.endswith("_authority")
    return {
        "kind": "adversarial_probe",
        "probe": "authority_overclaim",
        "claimed_authority": claimed_authority,
        "accepted": not unsafe,
        "reason": "blocked_by_boundary" if unsafe else "claim_not_blocked",
    }
