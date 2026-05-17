"""Unsat membranes for impossible constraint sets."""

from __future__ import annotations


def unsat_membrane(constraints: dict, unsat_core: list[str], relaxations: list[str]) -> dict:
    return {
        "kind": "parva_membrane",
        "membrane_kind": "unsat",
        "constraints": constraints,
        "unsat_core": unsat_core,
        "relaxations": relaxations,
        "review_required": True,
        "claim_boundary": "constraint_failure_not_generic_error",
    }
