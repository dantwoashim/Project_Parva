"""Replay verification dispatch for membrane artifacts."""

from __future__ import annotations

from typing import Any

from app.membranes.operation_verifiers.ad_to_bs import verify_ad_to_bs_replay
from app.membranes.operation_verifiers.bs_months import verify_bs_months_replay
from app.membranes.operation_verifiers.convert_bs_to_ad import verify_convert_bs_to_ad_replay
from app.membranes.operation_verifiers.fiscal_year import verify_fiscal_year_replay
from app.membranes.operation_verifiers.holiday import verify_holiday_replay
from app.membranes.operation_verifiers.validate_bs_date import verify_validate_bs_date_replay
from app.membranes.operation_verifiers.working_day import verify_working_day_replay


def replay_verify(membrane: dict[str, Any]) -> tuple[bool, str]:
    operation = str(membrane.get("canonical_query", {}).get("operation") or "")
    if operation == "convert_bs_to_ad":
        return verify_convert_bs_to_ad_replay(membrane)
    if operation == "ad_to_bs":
        return verify_ad_to_bs_replay(membrane)
    if operation == "validate_bs_date":
        return verify_validate_bs_date_replay(membrane)
    if operation == "holiday":
        return verify_holiday_replay(membrane)
    if operation == "working_day":
        return verify_working_day_replay(membrane)
    if operation == "fiscal_year":
        return verify_fiscal_year_replay(membrane)
    if operation == "bs_months":
        return verify_bs_months_replay(membrane)
    return False, "unsupported_operation_replay"


__all__ = ["replay_verify"]
