"""Shared OpenAPI schemas for Parva proof artifacts."""

from __future__ import annotations

from typing import Any


def add_proof_schemas(schema: dict[str, Any]) -> None:
    components = schema.setdefault("components", {}).setdefault("schemas", {})
    components.setdefault(
        "BoundaryVector",
        {
            "type": "object",
            "title": "BoundaryVector",
            "properties": {
                "authority": {"type": "string"},
                "claim_boundary": {"type": "string"},
                "review_state": {"type": "string"},
                "blocked_use_cases": {"type": "array", "items": {"type": "string"}},
                "warnings": {"type": "array", "items": {"type": "string"}},
                "not_authority": {"type": "boolean"},
                "not_panchanga_authority": {"type": "boolean"},
            },
        },
    )
    components.setdefault(
        "FieldProvenance",
        {
            "type": "object",
            "title": "FieldProvenance",
            "properties": {
                "field_path": {"type": "string"},
                "authority": {"type": "string"},
                "derivation": {"type": "string"},
                "source_docket_id": {"type": "string", "nullable": True},
                "witness_ids": {"type": "array", "items": {"type": "string"}},
                "policy_id": {"type": "string"},
                "review_state": {"type": "string"},
                "flags": {"type": "array", "items": {"type": "string"}},
            },
        },
    )
    components.setdefault(
        "MethodDocket",
        {
            "type": "object",
            "title": "MethodDocket",
            "properties": {
                "method_id": {"type": "string"},
                "algorithm": {"type": "string"},
                "implementation_version": {"type": "string"},
                "precision_tolerance": {"type": "string"},
                "assumptions": {"type": "array", "items": {"type": "string"}},
                "limitations": {"type": "array", "items": {"type": "string"}},
            },
        },
    )
    components.setdefault(
        "EphemerisProviderMetadata",
        {
            "type": "object",
            "title": "EphemerisProviderMetadata",
            "properties": {
                "provider_id": {"type": "string"},
                "provider_kind": {"type": "string"},
                "ephemeris_name": {"type": "string"},
                "ephemeris_version": {"type": "string"},
                "kernel_hash": {"type": "string", "nullable": True},
                "supported_date_range": {"type": "string"},
                "fallback_used": {"type": "boolean"},
                "jpl_backed": {"type": "boolean"},
            },
        },
    )
    components.setdefault(
        "PolicyDecisionTrace",
        {
            "type": "object",
            "title": "PolicyDecisionTrace",
            "properties": {
                "policy_id": {"type": "string"},
                "operation": {"type": "string"},
                "decision": {"type": "object"},
                "rules": {"type": "array", "items": {"type": "string"}},
                "notes": {"type": "array", "items": {"type": "string"}},
            },
        },
    )
    components.setdefault(
        "ProofReceipt",
        {
            "type": "object",
            "title": "ProofReceipt",
            "properties": {
                "mode": {"type": "string", "enum": ["compact", "audit", "replay", "membrane"]},
                "identity_hash": {"type": "string"},
                "witness_hash": {"type": "string"},
                "boundary_vector": {"$ref": "#/components/schemas/BoundaryVector"},
                "field_provenance": {
                    "type": "object",
                    "additionalProperties": {"$ref": "#/components/schemas/FieldProvenance"},
                },
                "source_docket_refs": {"type": "array", "items": {"type": "string"}},
                "proof_pack": {"type": "object"},
            },
        },
    )
    components.setdefault(
        "ProofPack",
        {
            "type": "object",
            "title": "ProofPack",
            "properties": {
                "kind": {"type": "string", "example": "parva_proofpack"},
                "proofpack_version": {"type": "string"},
                "level": {"type": "string"},
                "identity_hash": {"type": "string"},
                "witness_hash": {"type": "string"},
                "boundary": {"$ref": "#/components/schemas/BoundaryVector"},
                "membrane": {"type": "object"},
            },
        },
    )
    components.setdefault(
        "Timepack",
        {
            "type": "object",
            "title": "Timepack",
            "properties": {
                "kind": {"type": "string", "example": "parva_timepack"},
                "timepack_version": {"type": "string"},
                "artifact_type": {"type": "string"},
                "proof_packs": {"type": "array", "items": {"$ref": "#/components/schemas/ProofPack"}},
                "aggregate_witness_hash": {"type": "string"},
                "boundary_summary": {"$ref": "#/components/schemas/BoundaryVector"},
                "result_summary": {"type": "object"},
                "replay_instructions": {"type": "string"},
            },
        },
    )
    components.setdefault(
        "PayrollDateRiskReport",
        {
            "type": "object",
            "title": "PayrollDateRiskReport",
            "properties": {
                "kind": {"type": "string"},
                "summary": {"type": "object"},
                "findings": {"type": "array", "items": {"type": "object"}},
                "claim_boundary": {"type": "string"},
                "not_authority": {"type": "boolean"},
            },
        },
    )
