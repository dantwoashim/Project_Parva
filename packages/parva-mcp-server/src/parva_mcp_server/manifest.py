"""MCP descriptor for public-safe Parva temporal tools."""

from __future__ import annotations

import hashlib
import json
from typing import Any

RESOURCES = (
    "parva://capabilities",
    "parva://route-maturity",
    "parva://source-policy",
    "parva://supported-ranges",
    "parva://known-limitations",
    "parva://benchmark-summary",
)

TOOLS = (
    {"name": "convert_bs_to_ad", "route": "/v3/api/calendar/bs-to-gregorian", "method": "POST"},
    {"name": "convert_ad_to_bs", "route": "/v3/api/calendar/convert", "method": "GET"},
    {"name": "get_nepali_today", "route": "/v3/api/calendar/today", "method": "GET"},
    {"name": "check_holiday", "route": "/v3/api/compliance/evaluate-date", "method": "POST"},
    {"name": "check_working_day", "route": "/v3/api/compliance/evaluate-date", "method": "POST"},
    {"name": "get_fiscal_year", "route": "/v3/api/enterprise/fiscal-year/{bs_year}", "method": "GET"},
    {"name": "get_festival_date", "route": "/v3/api/festivals/{festival_id}", "method": "GET"},
    {"name": "get_panchanga_summary", "route": "/v3/api/calendar/panchanga", "method": "GET"},
    {"name": "check_temporal_claim", "route": "/v3/api/agent/verify-claim", "method": "POST"},
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


def build_manifest() -> dict[str, Any]:
    manifest = {
        "schema_version": "2026-05-15.parva_mcp",
        "name": "parva-public-temporal-tools",
        "read_only": True,
        "core_runtime_required": False,
        "authority_boundary": (
            "Parva MCP is decision support only. It is not official government, "
            "legal, tax, banking, payroll, future-date, or religious authority."
        ),
        "resources": [{"uri": uri, "read_only": True} for uri in RESOURCES],
        "tools": [
            {
                **tool,
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
    for tool in payload.get("tools", []):
        route = str(tool.get("route", "")).lower()
        if not route.startswith("/v3/api/"):
            issues.append(f"{tool.get('name')}: route must stay on public-safe v3 API")
        for fragment in FORBIDDEN_FRAGMENTS:
            if fragment in route:
                issues.append(f"{tool.get('name')}: forbidden route fragment {fragment}")
        if tool.get("read_only") is not True:
            issues.append(f"{tool.get('name')}: tool must be read-only")
    security = payload.get("security", {})
    for key in (
        "shell_execution",
        "filesystem_writes",
        "private_routes",
        "admin_routes",
        "billing_routes",
        "trust_mutation_routes",
        "exact_unsupported_future_bs_predictions",
    ):
        if security.get(key) is not False:
            issues.append(f"security.{key} must be false")
    return issues
