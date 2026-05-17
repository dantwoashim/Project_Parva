"""Replay verifier for AD-to-BS membranes."""

from __future__ import annotations

from datetime import date
from typing import Any

from app.calendar.bikram_sambat import gregorian_to_bs
from app.membranes.operation_verifiers.common import verify_common_replay
from app.membranes.source_resolution import resolve_ad_to_bs_source


def verify_ad_to_bs_replay(membrane: dict[str, Any]) -> tuple[bool, str]:
    try:
        raw_date = str(membrane["canonical_query"]["input"]["ad_date"])
        ad_date = date.fromisoformat(raw_date)
    except (KeyError, TypeError, ValueError):
        return False, "canonical_query_input_invalid"
    year, month, day = gregorian_to_bs(ad_date)
    expected = {
        "bs_date": f"{year:04d}-{month:02d}-{day:02d}",
        "year": year,
        "month": month,
        "day": day,
    }
    return verify_common_replay(
        membrane,
        operation="ad_to_bs",
        replay_step="ad_to_bs",
        expected_result=expected,
        expected_source_resolution=lambda: resolve_ad_to_bs_source(year, month, day),
    )


__all__ = ["verify_ad_to_bs_replay"]
