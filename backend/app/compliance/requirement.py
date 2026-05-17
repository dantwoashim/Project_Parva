"""Requirement object."""

from __future__ import annotations


def document_requirement(name: str, required: bool = True) -> dict:
    return {"name": name, "required": required, "claim_type": "document_requirement_claim"}
