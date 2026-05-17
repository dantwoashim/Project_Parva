"""Replay verifier for fiscal-year membranes."""

from __future__ import annotations

from typing import Any

from app.membranes.operation_verifiers.common import verify_common_replay
from app.membranes.source_resolution import resolve_fiscal_year_source
from app.services.enterprise_calendar_service import fiscal_year_payload


def _expected(bs_year: int) -> dict[str, Any]:
    payload = fiscal_year_payload(bs_year, trace_id=None)
    return {
        "fiscal_year": payload["fiscal_year"],
        "start": payload["start"],
        "end": payload["end"],
        "basis": payload["basis"],
    }


def verify_fiscal_year_replay(membrane: dict[str, Any]) -> tuple[bool, str]:
    try:
        bs_year = int(membrane["canonical_query"]["input"]["bs_year"])
    except (KeyError, TypeError, ValueError):
        return False, "canonical_query_input_invalid"
    return verify_common_replay(
        membrane,
        operation="fiscal_year",
        replay_step="fiscal_year_rule",
        expected_result=_expected(bs_year),
        expected_source_resolution=lambda: resolve_fiscal_year_source(bs_year),
    )


__all__ = ["verify_fiscal_year_replay"]
