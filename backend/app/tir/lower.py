"""Lower TemporalIR into canonical query."""

from __future__ import annotations

from app.canonicalization.normalize import canonicalize_query
from app.tir.schema import TemporalIR


def lower_to_canonical(ir: TemporalIR) -> dict:
    payload = {"operation": ir.intent, "input": {entity["type"]: entity["value"] for entity in ir.entities}}
    for constraint in ir.constraints:
        payload["input"][constraint["type"]] = constraint["value"]
    return canonicalize_query(payload)
