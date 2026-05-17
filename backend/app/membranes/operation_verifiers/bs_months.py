"""Replay verifier for BS month metadata membranes."""

from __future__ import annotations

from typing import Any

from app.membranes.operation_verifiers.common import verify_common_replay
from app.membranes.source_resolution import resolve_bs_months_source
from app.services.enterprise_calendar_service import bs_months_payload


def _expected(bs_year: int, mode: str) -> dict[str, Any]:
    payload = bs_months_payload(bs_year, mode=mode, trace_id=None)
    return {
        "bs_year": payload["bs_year"],
        "requested_mode": payload["requested_mode"],
        "selected_method": payload.get("selected_method"),
        "total_days": payload.get("total_days"),
        "months": payload.get("months"),
        "branch_set": payload.get("branch_set"),
        "branches": payload.get("branches"),
        "policy_decision": payload.get("policy_decision"),
    }


def verify_bs_months_replay(membrane: dict[str, Any]) -> tuple[bool, str]:
    try:
        payload = membrane["canonical_query"]["input"]
        bs_year = int(payload["bs_year"])
        mode = str(payload.get("mode") or "canonical")
    except (KeyError, TypeError, ValueError):
        return False, "canonical_query_input_invalid"
    return verify_common_replay(
        membrane,
        operation="bs_months",
        replay_step="bs_months_metadata",
        expected_result=_expected(bs_year, mode),
        expected_source_resolution=lambda: resolve_bs_months_source(bs_year, mode),
    )


__all__ = ["verify_bs_months_replay"]
