"""Federated witness challenge workflow."""

from __future__ import annotations


def challenge_object(challenged_witness: str, reason: str, counter_witness: dict) -> dict:
    return {
        "challenged_witness": challenged_witness,
        "reason": reason,
        "counter_witness": counter_witness,
        "status": "open",
        "resolution": None,
    }
