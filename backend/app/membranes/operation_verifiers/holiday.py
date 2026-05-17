"""Replay verifier for holiday membership membranes."""

from __future__ import annotations

from typing import Any

from app.membranes.capsule import _holiday_result
from app.membranes.operation_verifiers.common import verify_common_replay
from app.membranes.source_resolution import resolve_holiday_source


def verify_holiday_replay(membrane: dict[str, Any]) -> tuple[bool, str]:
    try:
        payload = membrane["canonical_query"]["input"]
        year = int(payload["year"])
        month = int(payload["month"])
        day = int(payload["day"])
        profile_id = str(payload.get("profile_id") or "nepal_public_general")
    except (KeyError, TypeError, ValueError):
        return False, "canonical_query_input_invalid"
    return verify_common_replay(
        membrane,
        operation="holiday",
        replay_step="holiday_membership",
        expected_result=_holiday_result(year, month, day, profile_id),
        expected_source_resolution=lambda: resolve_holiday_source(year, month, day),
    )


__all__ = ["verify_holiday_replay"]
