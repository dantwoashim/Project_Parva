"""Branch membranes for polyphonic temporal claims."""

from __future__ import annotations


def branch_set_membrane(branches: list[dict]) -> dict:
    return {
        "kind": "parva_membrane",
        "membrane_kind": "branch_set",
        "branches": branches,
        "review_required": True,
        "claim_boundary": "polyphonic_branches_not_single_authority",
    }
