"""Structured conflict membranes."""

from __future__ import annotations


def contradiction_membrane(left: dict, right: dict, reason: str) -> dict:
    return {
        "kind": "parva_membrane",
        "membrane_kind": "contradiction",
        "status": "source_conflict",
        "branches": [left, right],
        "reason": reason,
        "review_required": True,
    }
