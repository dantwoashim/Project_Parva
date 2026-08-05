"""Canonical descriptor for Project Parva's public MCP surface."""

from __future__ import annotations

import hashlib
import json
from typing import Any

AGENT_GATEWAY_ROUTE = "/v3/api/agent/run-tool"
DEFAULT_PUBLIC_ORIGIN = "https://api.prabinghimire1.com.np"

RESOURCES = (
    "parva://capabilities",
    "parva://route-maturity",
    "parva://source-policy",
    "parva://supported-ranges",
    "parva://known-limitations",
    "parva://benchmark-summary",
)

PROMPTS = (
    "explain_nepali_date_safely",
    "check_claim_with_sources",
    "plan_schedule_with_review_gates",
)

FORBIDDEN_FRAGMENTS = (
    "/admin/",
    "/billing/",
    "/keys",
    "/webhooks",
    "/trust/mutate",
    "future-bs/month-lengths",
    "future-bs/backtest",
    "future-bs/export",
    "future-bs/model-runs",
    "loan-impact",
    "calendar-model-risk/prediction",
    "audit-external-sheet",
    "stress-test",
)

DATE_SCHEMA: dict[str, Any] = {
    "type": "string",
    "format": "date",
    "pattern": r"^\d{4}-\d{2}-\d{2}$",
    "description": "Date in YYYY-MM-DD format.",
}

DATE_PAIR_PROPERTIES: dict[str, Any] = {
    "ad_date": {
        **DATE_SCHEMA,
        "description": "Gregorian date in YYYY-MM-DD format.",
    },
    "bs_date": {
        "type": "string",
        "pattern": r"^\d{4}-\d{2}-\d{2}$",
        "description": "Bikram Sambat date in YYYY-MM-DD format.",
    },
    "profile_id": {
        "type": "string",
        "minLength": 1,
        "maxLength": 120,
        "default": "nepal_private_company_default",
        "description": "Public compliance profile id.",
    },
}

DATE_PAIR_ONE_OF = [
    {"required": ["ad_date"]},
    {"required": ["bs_date"]},
]

OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["claim_boundary", "review_required", "not_authority"],
    "properties": {
        "claim_boundary": {"type": "string"},
        "review_required": {"type": "boolean"},
        "not_authority": {"type": "boolean"},
    },
    "additionalProperties": True,
}

TOOLS: tuple[dict[str, Any], ...] = (
    {
        "name": "convert_bs_to_ad",
        "title": "Convert BS to AD",
        "description": (
            "Convert a supported Bikram Sambat date to Gregorian and return source, "
            "confidence, and review metadata."
        ),
        "agent_tool": "parva.convert_date",
        "input_schema": {
            "type": "object",
            "properties": {
                "year": {
                    "type": "integer",
                    "minimum": 1900,
                    "maximum": 2200,
                    "description": "Bikram Sambat year.",
                },
                "month": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 12,
                    "description": "Bikram Sambat month number.",
                },
                "day": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 32,
                    "description": "Bikram Sambat day number.",
                },
            },
            "required": ["year", "month", "day"],
            "additionalProperties": False,
        },
    },
    {
        "name": "convert_ad_to_bs",
        "title": "Convert AD to BS",
        "description": (
            "Convert a Gregorian date to Bikram Sambat and return source, confidence, "
            "and review metadata."
        ),
        "agent_tool": "parva.convert_date",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {
                    **DATE_SCHEMA,
                    "description": "Gregorian date in YYYY-MM-DD format.",
                }
            },
            "required": ["date"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_nepali_today",
        "title": "Get Today's Nepali Date",
        "description": "Return today's Gregorian and Bikram Sambat calendar context for Nepal.",
        "agent_tool": "parva.get_today",
        "input_schema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "name": "check_holiday",
        "title": "Check Holiday",
        "description": (
            "Evaluate whether one AD or BS date matches a holiday under a public "
            "institution profile."
        ),
        "agent_tool": "parva.evaluate_compliance_date",
        "input_schema": {
            "type": "object",
            "properties": DATE_PAIR_PROPERTIES,
            "oneOf": DATE_PAIR_ONE_OF,
            "additionalProperties": False,
        },
    },
    {
        "name": "check_working_day",
        "title": "Check Working Day",
        "description": (
            "Evaluate working-day status for one AD or BS date while preserving "
            "institutional review gates."
        ),
        "agent_tool": "parva.evaluate_compliance_date",
        "input_schema": {
            "type": "object",
            "properties": {
                **DATE_PAIR_PROPERTIES,
                "decision_intent": {
                    "type": "string",
                    "enum": ["general", "payroll", "banking"],
                    "default": "general",
                    "description": "Decision context used to apply review gates.",
                },
            },
            "oneOf": DATE_PAIR_ONE_OF,
            "additionalProperties": False,
        },
    },
    {
        "name": "get_fiscal_year",
        "title": "Get Nepali Fiscal Period",
        "description": (
            "Return the Nepali fiscal year, month, and quarter for one AD or BS date."
        ),
        "agent_tool": "parva.get_fiscal_period",
        "input_schema": {
            "type": "object",
            "properties": DATE_PAIR_PROPERTIES,
            "oneOf": DATE_PAIR_ONE_OF,
            "additionalProperties": False,
        },
    },
    {
        "name": "get_festival_date",
        "title": "Get Festival Date",
        "description": (
            "Calculate a supported festival's date range for one Gregorian year."
        ),
        "agent_tool": "parva.get_festival_date",
        "input_schema": {
            "type": "object",
            "properties": {
                "festival_id": {
                    "type": "string",
                    "pattern": r"^[a-z0-9][a-z0-9-]{0,79}$",
                    "description": "Public festival slug, such as dashain or tihar.",
                },
                "year": {
                    "type": "integer",
                    "minimum": 2000,
                    "maximum": 2100,
                    "description": "Gregorian year used for the calculation.",
                },
            },
            "required": ["festival_id", "year"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_panchanga_summary",
        "title": "Get Panchanga Summary",
        "description": (
            "Return tithi, nakshatra, yoga, karana, vaara, and observation context "
            "for one Gregorian date."
        ),
        "agent_tool": "parva.get_panchanga_summary",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {
                    **DATE_SCHEMA,
                    "description": "Gregorian date in YYYY-MM-DD format.",
                },
                "latitude": {
                    "type": "number",
                    "minimum": -90,
                    "maximum": 90,
                    "default": 27.7172,
                    "description": "Observer latitude in decimal degrees.",
                },
                "longitude": {
                    "type": "number",
                    "minimum": -180,
                    "maximum": 180,
                    "default": 85.324,
                    "description": "Observer longitude in decimal degrees.",
                },
                "timezone": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 80,
                    "default": "Asia/Kathmandu",
                    "description": "IANA timezone name used for civil time.",
                },
                "ayanamsa": {
                    "type": "string",
                    "enum": ["lahiri", "raman", "kp"],
                    "default": "lahiri",
                    "description": "Sidereal ayanamsa profile.",
                },
                "risk_mode": {
                    "type": "string",
                    "enum": ["standard", "strict"],
                    "default": "standard",
                    "description": "Boundary-risk reporting mode.",
                },
            },
            "required": ["date"],
            "additionalProperties": False,
        },
    },
    {
        "name": "check_temporal_claim",
        "title": "Check Temporal Claim",
        "description": (
            "Verify a supported BS/AD temporal claim and return evidence and human-review status."
        ),
        "agent_tool": "parva.verify_temporal_claim",
        "input_schema": {
            "type": "object",
            "properties": {
                "claim": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 2000,
                    "description": "Temporal claim to verify.",
                },
                "context": {
                    "type": "object",
                    "maxProperties": 32,
                    "description": "Optional bounded context for claim interpretation.",
                },
                "include_evidence": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include public evidence metadata when available.",
                },
            },
            "required": ["claim"],
            "additionalProperties": False,
        },
    },
)


def build_manifest() -> dict[str, Any]:
    manifest = {
        "schema_version": "2026-07-20.parva_mcp.v1",
        "name": "parva-public-temporal-tools",
        "read_only": True,
        "core_runtime_required": False,
        "execution": {
            "mode": "http_agent_gateway",
            "route": AGENT_GATEWAY_ROUTE,
            "method": "POST",
        },
        "authority_boundary": (
            "Parva MCP is decision support only. It is not official government, "
            "legal, tax, banking, payroll, future-date, or religious authority."
        ),
        "resources": [{"uri": uri, "read_only": True} for uri in RESOURCES],
        "tools": [
            {
                **tool,
                "route": AGENT_GATEWAY_ROUTE,
                "method": "POST",
                "output_schema": OUTPUT_SCHEMA,
                "read_only": True,
                "claim_boundary": "decision_support_not_authority",
                "review_required_passthrough": True,
            }
            for tool in TOOLS
        ],
        "prompts": [{"name": name, "safety_bound": True} for name in PROMPTS],
        "security": {
            "shell_execution": False,
            "filesystem_writes": False,
            "private_routes": False,
            "admin_routes": False,
            "billing_routes": False,
            "trust_mutation_routes": False,
            "exact_unsupported_future_bs_predictions": False,
            "redirects": False,
            "bounded_http_timeout": True,
            "bounded_response_size": True,
        },
    }
    manifest["manifest_sha256"] = manifest_digest(manifest, include_digest=False)
    return manifest


def manifest_digest(manifest: dict[str, Any] | None = None, *, include_digest: bool = True) -> str:
    payload = dict(manifest or build_manifest())
    if not include_digest:
        payload.pop("manifest_sha256", None)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def lint_manifest(manifest: dict[str, Any] | None = None) -> list[str]:
    payload = manifest or build_manifest()
    issues: list[str] = []
    if payload.get("read_only") is not True:
        issues.append("manifest must be read-only")
    names: set[str] = set()
    for tool in payload.get("tools", []):
        name = str(tool.get("name", ""))
        route = str(tool.get("route", ""))
        if not name or name in names:
            issues.append(f"duplicate or empty tool name: {name}")
        names.add(name)
        if route != AGENT_GATEWAY_ROUTE or tool.get("method") != "POST":
            issues.append(f"{name}: tool must use the agent gateway")
        for fragment in FORBIDDEN_FRAGMENTS:
            if fragment in route.lower():
                issues.append(f"{name}: forbidden route fragment {fragment}")
        schema = tool.get("input_schema")
        if not isinstance(schema, dict) or schema.get("type") != "object":
            issues.append(f"{name}: input_schema must be an object schema")
        elif "additionalProperties" not in schema:
            issues.append(f"{name}: input_schema must declare additionalProperties")
        if tool.get("read_only") is not True:
            issues.append(f"{name}: tool must be read-only")
    security = payload.get("security", {})
    for key in (
        "shell_execution",
        "filesystem_writes",
        "private_routes",
        "admin_routes",
        "billing_routes",
        "trust_mutation_routes",
        "exact_unsupported_future_bs_predictions",
        "redirects",
    ):
        if security.get(key) is not False:
            issues.append(f"security.{key} must be false")
    for key in ("bounded_http_timeout", "bounded_response_size"):
        if security.get(key) is not True:
            issues.append(f"security.{key} must be true")
    return issues
