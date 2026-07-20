#!/usr/bin/env python3
"""Generate the static public-demo OpenAPI artifact used by docs mirrors."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from openapi_proof_schemas import add_proof_contract_references  # noqa: E402


def _output_path() -> Path:
    configured = os.getenv("PARVA_OPENAPI_OUTPUT", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return PROJECT_ROOT / "docs" / "api-docs" / "openapi.json"


def _write_schema(schema: dict) -> int:
    schema["servers"] = [
        {
            "url": os.getenv(
                "PARVA_PUBLIC_DEMO_SERVER",
                "https://api.prabinghimire1.com.np",
            ),
            "description": "Project Parva public API",
        }
    ]
    output_path = _output_path()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    try:
        rendered_path = output_path.relative_to(PROJECT_ROOT)
    except ValueError:
        rendered_path = output_path
    print(f"Wrote {rendered_path} with {len(schema.get('paths', {}))} paths.")
    return 0


def main() -> int:
    os.environ["PARVA_ROUTE_PROFILE"] = os.getenv("PARVA_ROUTE_PROFILE", "developer_preview")
    os.environ["PARVA_ENABLE_EXPERIMENTAL_API"] = "false"
    os.environ["PARVA_SHOW_PRIVATE_SCHEMA"] = "false"
    os.environ["PARVA_OPENAPI_SURFACE"] = "canonical"
    os.environ["PARVA_ENV"] = "public"
    os.environ["PARVA_SOURCE_URL"] = "https://github.com/dantwoashim/Project_Parva"
    os.environ["PARVA_ADMIN_TOKEN"] = "test-openapi-admin-token"
    os.environ["PARVA_PROVENANCE_ATTESTATION_KEY"] = "test-provenance-key"
    os.environ["PARVA_REQUIRE_PRECOMPUTED"] = "false"
    os.environ["PARVA_SERVE_FRONTEND"] = "false"
    os.environ.setdefault("PARVA_RATE_LIMIT_ENABLED", "false")

    from app.bootstrap.app_factory import create_app

    app = create_app()
    schema = app.openapi()
    if schema.get("x-parva-openapi-surface") == "canonical":
        return _write_schema(schema)

    add_proof_contract_references(schema)
    components = schema.setdefault("components", {}).setdefault("schemas", {})
    components.setdefault(
        "SourceAwareMeta",
        {
            "type": "object",
            "title": "SourceAwareMeta",
            "required": [
                "source",
                "confidence",
                "data_version",
                "release_id",
                "claim_boundary",
                "warnings",
                "trace_id",
            ],
            "properties": {
                "source": {
                    "type": "object",
                    "required": ["id", "label", "tier", "authority", "version"],
                    "properties": {
                        "id": {"type": "string"},
                        "label": {"type": "string"},
                        "tier": {"type": "string"},
                        "authority": {"type": "string"},
                        "version": {"type": "string"},
                        "url": {"type": "string", "nullable": True},
                        "retrieved_at": {"type": "string", "nullable": True},
                    },
                },
                "confidence": {"type": "string"},
                "data_version": {"type": "string"},
                "release_id": {"type": "string"},
                "claim_boundary": {"type": "string"},
                "warnings": {"type": "array", "items": {"type": "string"}},
                "trace_id": {"type": "string", "nullable": True},
                "result_class": {"type": "string"},
            },
        },
    )
    components.setdefault(
        "TemporalFact",
        {
            "type": "object",
            "title": "TemporalFact",
            "required": [
                "fact_id",
                "fact_type",
                "subject",
                "predicate",
                "object",
                "release_id",
                "source_ids",
                "confidence",
                "claim_boundary",
                "warnings",
            ],
            "properties": {
                "fact_id": {"type": "string", "example": "fact_bs_ad_2083_01_01"},
                "fact_type": {"type": "string", "example": "bs_ad_mapping"},
                "subject": {"type": "object"},
                "predicate": {"type": "string", "example": "maps_to"},
                "object": {"type": "object"},
                "release_id": {"type": "string", "example": "parva-bs-public-demo"},
                "source_ids": {"type": "array", "items": {"type": "string"}},
                "confidence": {"type": "string", "example": "official_verified"},
                "claim_boundary": {
                    "type": "string",
                    "example": "official_source_interpretation_not_legal_advice",
                },
                "warnings": {"type": "array", "items": {"type": "string"}},
                "jurisdiction": {"type": "string", "nullable": True},
                "profile_ids": {"type": "array", "items": {"type": "string"}},
                "validity": {"type": "object"},
                "metadata": {"type": "object"},
            },
        },
    )
    components.setdefault(
        "TimeGraphRelationship",
        {
            "type": "object",
            "title": "TimeGraphRelationship",
            "required": ["relationship_id", "from_id", "to_id", "type", "release_id", "confidence"],
            "properties": {
                "relationship_id": {"type": "string"},
                "from_id": {"type": "string"},
                "to_id": {"type": "string"},
                "type": {"type": "string", "example": "SUPPORTED_BY"},
                "release_id": {"type": "string"},
                "confidence": {"type": "string"},
                "metadata": {"type": "object"},
            },
        },
    )
    components.setdefault(
        "TimeGraphConflict",
        {
            "type": "object",
            "title": "TimeGraphConflict",
            "required": [
                "conflict_id",
                "conflict_type",
                "status",
                "facts",
                "sources",
                "release_ids",
                "summary",
                "resolution_policy",
                "requires_human_review",
                "confidence",
                "warnings",
            ],
            "properties": {
                "conflict_id": {"type": "string"},
                "conflict_type": {"type": "string"},
                "status": {"type": "string", "example": "fixture_only"},
                "facts": {"type": "array", "items": {"type": "string"}},
                "sources": {"type": "array", "items": {"type": "string"}},
                "release_ids": {"type": "array", "items": {"type": "string"}},
                "summary": {"type": "string"},
                "resolution_policy": {"type": "string"},
                "requires_human_review": {"type": "boolean"},
                "confidence": {"type": "string"},
                "warnings": {"type": "array", "items": {"type": "string"}},
                "metadata": {"type": "object"},
            },
        },
    )
    components.setdefault(
        "TimeGraphTrace",
        {
            "type": "object",
            "title": "TimeGraphTrace",
            "required": ["fact_id", "fact", "sources", "release", "relationships", "conflicts"],
            "properties": {
                "fact_id": {"type": "string"},
                "fact": {"$ref": "#/components/schemas/TemporalFact"},
                "sources": {"type": "array", "items": {"type": "object"}},
                "release": {"type": "object"},
                "derived_from": {"type": "array", "items": {"type": "object"}},
                "relationships": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/TimeGraphRelationship"},
                },
                "evidence_packets": {"type": "array", "items": {"type": "object"}},
                "conflicts": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/TimeGraphConflict"},
                },
                "confidence": {"type": "string"},
                "warnings": {"type": "array", "items": {"type": "string"}},
                "claim_boundary": {"type": "string"},
                "trace_depth": {"type": "integer"},
            },
        },
    )
    components.setdefault(
        "TimeGraphMetadata",
        {
            "type": "object",
            "title": "TimeGraphMetadata",
            "required": ["release_id", "confidence", "claim_boundary", "warnings"],
            "properties": {
                "release_id": {"type": "string"},
                "confidence": {"type": "string"},
                "claim_boundary": {"type": "string"},
                "warnings": {"type": "array", "items": {"type": "string"}},
                "trace_id": {"type": "string", "nullable": True},
            },
        },
    )
    components.setdefault(
        "RuleInputSchema",
        {
            "type": "object",
            "title": "RuleInputSchema",
            "required": ["type"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": [
                        "bs_date",
                        "ad_date",
                        "date",
                        "bs_month",
                        "ad_month",
                        "profile_id",
                        "integer",
                        "string",
                        "boolean",
                        "enum",
                    ],
                },
                "required": {"type": "boolean"},
                "default": {},
                "values": {"type": "array", "items": {}},
            },
        },
    )
    components.setdefault(
        "RuleRiskPolicy",
        {
            "type": "object",
            "title": "RuleRiskPolicy",
            "properties": {
                "require_confidence_at_least": {"type": "string", "example": "source_backed"},
                "block_research_preview": {"type": "boolean"},
                "block_disputed_facts": {"type": "boolean"},
                "unsupported_result_action": {"type": "string", "example": "human_review_required"},
                "future_date_action": {"type": "string", "example": "human_review_required"},
                "payroll_requires_official_or_source_backed": {"type": "boolean"},
            },
        },
    )
    components.setdefault(
        "RuleStep",
        {
            "type": "object",
            "title": "RuleStep",
            "description": "One structured RuleLang step. Exactly one of set, if, while, return, or call is used.",
            "properties": {
                "set": {"type": "object"},
                "if": {"type": "object"},
                "while": {"type": "object"},
                "return": {"type": "object"},
                "call": {"type": "object"},
            },
        },
    )
    components.setdefault(
        "RuleDefinition",
        {
            "type": "object",
            "title": "RuleDefinition",
            "required": [
                "rule_id",
                "version",
                "label",
                "description",
                "status",
                "inputs",
                "outputs",
                "steps",
                "risk_policy",
                "claim_boundary",
            ],
            "properties": {
                "rule_id": {"type": "string", "example": "last_working_day_of_nepali_month"},
                "version": {"type": "string", "example": "1.0.0"},
                "label": {"type": "string"},
                "description": {"type": "string"},
                "profile_id": {"type": "string", "example": "nepal_private_company_default"},
                "status": {"type": "string", "example": "public_preview"},
                "inputs": {
                    "type": "object",
                    "additionalProperties": {"$ref": "#/components/schemas/RuleInputSchema"},
                },
                "outputs": {"type": "object"},
                "steps": {"type": "array", "items": {"$ref": "#/components/schemas/RuleStep"}},
                "risk_policy": {"$ref": "#/components/schemas/RuleRiskPolicy"},
                "claim_boundary": {
                    "type": "string",
                    "example": "enterprise_decision_support_not_legal_authority",
                },
                "tests": {"type": "array", "items": {"type": "object"}},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
        },
    )
    components.setdefault(
        "RuleDecision",
        {
            "type": "object",
            "title": "RuleDecision",
            "required": ["status", "requires_human_review", "reason_codes"],
            "properties": {
                "status": {"type": "string", "example": "approved"},
                "requires_human_review": {"type": "boolean"},
                "reason_codes": {"type": "array", "items": {"type": "string"}},
            },
        },
    )
    components.setdefault(
        "RuleTraceStep",
        {
            "type": "object",
            "title": "RuleTraceStep",
            "properties": {
                "step_index": {"type": "integer"},
                "operation": {"type": "string"},
                "function": {"type": "string", "nullable": True},
                "arguments": {"type": "object"},
                "result": {},
                "fact_ids": {"type": "array", "items": {"type": "string"}},
                "confidence": {"type": "string", "nullable": True},
                "warnings": {"type": "array", "items": {"type": "string"}},
                "reason_codes": {"type": "array", "items": {"type": "string"}},
            },
        },
    )
    components.setdefault(
        "RuleTrace",
        {
            "type": "object",
            "title": "RuleTrace",
            "properties": {
                "steps": {"type": "array", "items": {"$ref": "#/components/schemas/RuleTraceStep"}},
                "bounded": {"type": "boolean"},
                "max_trace_steps": {"type": "integer"},
            },
        },
    )
    components.setdefault(
        "RuleExecutionResult",
        {
            "type": "object",
            "title": "RuleExecutionResult",
            "required": [
                "rule_id",
                "rule_version",
                "profile_id",
                "input",
                "output",
                "decision",
                "trace",
                "fact_ids",
                "release_id",
                "confidence",
                "claim_boundary",
                "warnings",
            ],
            "properties": {
                "rule_id": {"type": "string"},
                "rule_version": {"type": "string"},
                "profile_id": {"type": "string"},
                "input": {"type": "object"},
                "output": {"type": "object"},
                "decision": {"$ref": "#/components/schemas/RuleDecision"},
                "trace": {"$ref": "#/components/schemas/RuleTrace"},
                "fact_ids": {"type": "array", "items": {"type": "string"}},
                "evidence_packet_id": {"type": "string", "nullable": True},
                "release_id": {"type": "string"},
                "confidence": {"type": "string"},
                "claim_boundary": {"type": "string"},
                "warnings": {"type": "array", "items": {"type": "string"}},
                "meta": {"$ref": "#/components/schemas/SourceAwareMeta"},
            },
        },
    )
    components.setdefault(
        "RuleValidationResult",
        {
            "type": "object",
            "title": "RuleValidationResult",
            "required": ["valid", "reason_codes", "errors"],
            "properties": {
                "valid": {"type": "boolean"},
                "reason_codes": {"type": "array", "items": {"type": "string"}},
                "errors": {"type": "array", "items": {"type": "string"}},
                "meta": {"$ref": "#/components/schemas/SourceAwareMeta"},
            },
        },
    )
    components.setdefault(
        "RuleCapabilities",
        {
            "type": "object",
            "title": "RuleCapabilities",
            "properties": {
                "surface": {"type": "string", "example": "parva_rulelang"},
                "status": {"type": "string", "example": "public_preview"},
                "publication_status": {
                    "type": "string",
                    "example": "computed_prediction_not_official",
                },
                "builtins": {"type": "array", "items": {"type": "string"}},
                "safety_limits": {"type": "object"},
                "not_allowed": {"type": "array", "items": {"type": "string"}},
                "reason_codes": {"type": "object"},
            },
        },
    )
    components.setdefault(
        "RuleError",
        {
            "type": "object",
            "title": "RuleError",
            "properties": {
                "code": {"type": "string", "example": "RULE_VALIDATION_FAILED"},
                "message": {"type": "string"},
                "details": {"type": "array", "items": {"type": "string"}},
            },
        },
    )
    preview_components = [
        "TemporalChangeSet",
        "TemporalChange",
        "SemanticReleaseDiff",
        "DependencyRecord",
        "ImpactRun",
        "ImpactItem",
        "ImpactEventPayload",
        "ImpactCapabilities",
        "AgentToolDefinition",
        "AgentCapabilities",
        "TemporalIntentRequest",
        "TemporalIntentResult",
        "TemporalClaimRequest",
        "TemporalClaimVerification",
        "SchedulePlanRequest",
        "SchedulePlanResult",
        "AgentExplanationRequest",
        "AgentExplanationResult",
        "HumanReviewCheck",
        "AgentDecision",
        "AgentToolManifest",
        "AgentBenchmarkCase",
        "AgentBenchmarkResult",
        "ProtocolVersion",
        "ProtocolCapabilities",
        "ProtocolSpecIndex",
        "ProtocolSchemaIndex",
        "CompatibilityLevel",
        "ConformanceRequest",
        "ConformanceReport",
        "CalendarCredential",
        "CredentialProof",
        "CredentialVerificationResult",
        "OfflineBundleManifest",
        "ProtocolRegistryEntry",
        "ProtocolGovernancePolicy",
    ]
    for component_name in preview_components:
        components.setdefault(
            component_name,
            {
                "type": "object",
                "title": component_name,
                "description": "Public preview contract schema for Project Parva temporal infrastructure.",
                "properties": {
                    "publication_status": {
                        "type": "string",
                        "example": "computed_prediction_not_official",
                    },
                    "claim_boundary": {"type": "string"},
                    "meta": {"type": "object"},
                },
                "additionalProperties": True,
            },
        )
    return _write_schema(schema)


if __name__ == "__main__":
    raise SystemExit(main())
