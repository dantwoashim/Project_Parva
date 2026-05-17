"""Replay verifier for BS date validation membranes."""

from __future__ import annotations

from typing import Any

from app.calendar.bikram_sambat import days_in_bs_month, is_valid_bs_date
from app.membranes.operation_verifiers.common import verify_common_replay
from app.membranes.source_resolution import resolve_validate_bs_date_source


def _expected(year: int, month: int, day: int) -> dict[str, Any]:
    try:
        max_day = days_in_bs_month(year, month)
    except ValueError as exc:
        return {
            "valid": False,
            "bs_date": f"{year:04d}-{month:02d}-{day:02d}",
            "reason": str(exc),
            "year": year,
            "month": month,
            "day": day,
            "max_day": None,
        }
    valid = is_valid_bs_date(year, month, day)
    return {
        "valid": valid,
        "bs_date": f"{year:04d}-{month:02d}-{day:02d}",
        "reason": "valid" if valid else f"day must be between 1 and {max_day}",
        "year": year,
        "month": month,
        "day": day,
        "max_day": max_day,
    }


def verify_validate_bs_date_replay(membrane: dict[str, Any]) -> tuple[bool, str]:
    try:
        payload = membrane["canonical_query"]["input"]
        year, month, day = int(payload["year"]), int(payload["month"]), int(payload["day"])
    except (KeyError, TypeError, ValueError):
        return False, "canonical_query_input_invalid"
    return verify_common_replay(
        membrane,
        operation="validate_bs_date",
        replay_step="validate_bs_date",
        expected_result=_expected(year, month, day),
        expected_source_resolution=lambda: resolve_validate_bs_date_source(year, month, day),
    )


__all__ = ["verify_validate_bs_date_replay"]
