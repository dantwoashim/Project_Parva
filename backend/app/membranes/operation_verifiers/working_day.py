"""Replay verifier for working-day decision membranes."""

from __future__ import annotations

from typing import Any

from app.membranes.capsule import _working_day_result
from app.membranes.operation_verifiers.common import verify_common_replay
from app.membranes.source_resolution import resolve_working_day_source


def verify_working_day_replay(membrane: dict[str, Any]) -> tuple[bool, str]:
    try:
        payload = membrane["canonical_query"]["input"]
        year = int(payload["year"])
        month = int(payload["month"])
        day = int(payload["day"])
        profile_id = str(payload.get("profile_id") or "nepal_private_company_default")
        decision_intent = str(payload.get("decision_intent") or "general")
    except (KeyError, TypeError, ValueError):
        return False, "canonical_query_input_invalid"
    return verify_common_replay(
        membrane,
        operation="working_day",
        replay_step="working_day_policy",
        expected_result=_working_day_result(year, month, day, profile_id, decision_intent),
        expected_source_resolution=lambda: resolve_working_day_source(year, month, day),
    )


__all__ = ["verify_working_day_replay"]
