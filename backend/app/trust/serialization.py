"""Serialization guardrails for trust-integrated outputs."""

from __future__ import annotations

from typing import Any

from app.trust.field_provenance import ProvenanceMap


def serialize_trust_result(result: dict[str, Any], provenance: ProvenanceMap) -> dict[str, Any]:
    """Serialize a result only after every top-level field has provenance."""

    provenance.require_all_fields(result)
    provenance.require_source_backed_dockets()
    return {
        "result": result,
        "field_provenance": provenance.as_dict(),
        "weakest_authority": provenance.weakest_authority().value,
    }
