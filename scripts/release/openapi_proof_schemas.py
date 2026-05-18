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
        "SourceDocketRef",
        {
            "type": "object",
            "title": "SourceDocketRef",
            "properties": {
                "source_docket_id": {"type": "string"},
                "authority": {"type": "string"},
                "coverage_status": {"type": "string"},
                "snapshot_hash": {"type": "string", "nullable": True},
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
                "capsule": {"$ref": "#/components/schemas/MembraneArtifact"},
            },
        },
    )
    components.setdefault(
        "MembraneArtifact",
        {
            "type": "object",
            "title": "MembraneArtifact",
            "properties": {
                "kind": {"type": "string", "example": "parva_membrane"},
                "membrane_kind": {"type": "string", "enum": ["positive", "negative", "branch", "unsat"]},
                "canonical_query": {"type": "object"},
                "identity_hash": {"type": "string"},
                "witness_hash": {"type": "string"},
                "result": {"type": "object"},
                "boundary": {"$ref": "#/components/schemas/BoundaryVector"},
                "field_provenance": {
                    "type": "object",
                    "additionalProperties": {"$ref": "#/components/schemas/FieldProvenance"},
                },
                "policy_trace": {"$ref": "#/components/schemas/PolicyDecisionTrace"},
            },
        },
    )
    components.setdefault(
        "ReplayStatus",
        {
            "type": "object",
            "title": "ReplayStatus",
            "properties": {
                "verified": {"type": "boolean"},
                "reason": {"type": "string"},
                "verifier": {"type": "string"},
            },
        },
    )
    components.setdefault(
        "NegativeMembrane",
        {"allOf": [{"$ref": "#/components/schemas/MembraneArtifact"}], "title": "NegativeMembrane"},
    )
    components.setdefault(
        "UnsatMembrane",
        {"allOf": [{"$ref": "#/components/schemas/MembraneArtifact"}], "title": "UnsatMembrane"},
    )
    components.setdefault(
        "BranchMembrane",
        {"allOf": [{"$ref": "#/components/schemas/MembraneArtifact"}], "title": "BranchMembrane"},
    )
    components.setdefault(
        "PanchangaProofArtifact",
        {
            "type": "object",
            "title": "PanchangaProofArtifact",
            "properties": {
                "proof": {"$ref": "#/components/schemas/ProofReceipt"},
                "method_dockets": {"type": "array", "items": {"$ref": "#/components/schemas/MethodDocket"}},
                "ephemeris_metadata": {"$ref": "#/components/schemas/EphemerisProviderMetadata"},
                "not_panchanga_authority": {"type": "boolean"},
                "not_ritual_final_authority": {"type": "boolean"},
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


PROOF_CAPABLE_PATHS = {
    "/v3/api/calendar/bs-to-gregorian",
    "/v3/api/calendar/convert",
    "/v3/api/calendar/validate-bs-date",
    "/v3/api/compliance/holiday",
    "/v3/api/compliance/evaluate-date",
    "/v3/api/enterprise/fiscal-year/{bs_year}",
    "/v3/api/enterprise/bs-months/{bs_year}",
    "/v3/api/calendar/panchanga",
}


def add_proof_contract_references(schema: dict[str, Any]) -> None:
    """Attach proof parameters and response references to proof-capable routes."""

    add_proof_schemas(schema)
    proof_parameter = {
        "name": "proof",
        "in": "query",
        "required": False,
        "schema": {"type": "string", "enum": ["none", "compact", "audit", "replay", "membrane"]},
        "description": "Optional proof level. Use none for no proof payload; compact/audit/replay/membrane return a proof receipt.",
    }
    for path, methods in schema.get("paths", {}).items():
        if path not in PROOF_CAPABLE_PATHS:
            continue
        for operation in methods.values():
            parameters = operation.setdefault("parameters", [])
            proof_params = [param for param in parameters if param.get("name") == "proof" and param.get("in") == "query"]
            if proof_params:
                for param in proof_params:
                    param["schema"] = proof_parameter["schema"]
                    param["description"] = proof_parameter["description"]
            else:
                parameters.append(proof_parameter)
            operation.setdefault("x-parva-proof-schemas", [])
            operation["x-parva-proof-schemas"] = [
                "#/components/schemas/ProofReceipt",
                "#/components/schemas/MembraneArtifact",
                "#/components/schemas/BoundaryVector",
                "#/components/schemas/FieldProvenance",
                "#/components/schemas/ReplayStatus",
            ]
            if "panchanga" in path:
                operation["x-parva-proof-schemas"].extend(
                    [
                        "#/components/schemas/PanchangaProofArtifact",
                        "#/components/schemas/MethodDocket",
                        "#/components/schemas/EphemerisProviderMetadata",
                    ]
                )
            responses = operation.setdefault("responses", {})
            ok = responses.setdefault("200", {}).setdefault("content", {}).setdefault("application/json", {})
            existing_schema = ok.get("schema", {"type": "object"})
            ok["schema"] = {
                "allOf": [
                    existing_schema,
                    {
                        "type": "object",
                        "properties": {
                            "proof": {"$ref": "#/components/schemas/ProofReceipt"},
                            "replay_status": {"$ref": "#/components/schemas/ReplayStatus"},
                        },
                    },
                ]
            }
