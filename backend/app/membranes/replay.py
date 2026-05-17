"""Replay verification dispatch for membrane artifacts."""

from __future__ import annotations

from typing import Any

from app.membranes.operation_verifiers.convert_bs_to_ad import verify_convert_bs_to_ad_replay


def replay_verify(membrane: dict[str, Any]) -> tuple[bool, str]:
    operation = str(membrane.get("canonical_query", {}).get("operation") or "")
    if operation == "convert_bs_to_ad":
        return verify_convert_bs_to_ad_replay(membrane)
    return False, "unsupported_operation_replay"


__all__ = ["replay_verify"]
