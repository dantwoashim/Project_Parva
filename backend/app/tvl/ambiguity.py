"""Ambiguity helpers for TVL."""

from __future__ import annotations


def ambiguity_set(candidates: list[dict]) -> dict:
    return {
        "kind": "ambiguity_set",
        "candidates": candidates[:3],
        "requires_confirmation": len(candidates) != 1,
    }
