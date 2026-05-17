"""Portable timepack wrapper."""

from __future__ import annotations

from app.membranes.proofpack import proof_pack


def build_timepack(membrane: dict, level: str) -> dict:
    return {
        "kind": "parva_timepack",
        "level": level,
        "payload": proof_pack(membrane, level),
    }
