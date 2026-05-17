"""Process object."""

from __future__ import annotations


def process_object(process_id: str, steps: list[str]) -> dict:
    return {"process_id": process_id, "steps": steps, "claim_boundary": "planning_support_not_authority"}
