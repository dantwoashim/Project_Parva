"""Composed membrane lineage."""

from __future__ import annotations


def compose_membrane(parent_id: str, child_ids: list[str], result: dict) -> dict:
    return {
        "kind": "parva_membrane",
        "membrane_kind": "composition",
        "parent_id": parent_id,
        "child_membranes": child_ids,
        "result": result,
    }
