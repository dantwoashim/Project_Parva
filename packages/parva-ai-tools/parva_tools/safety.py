"""Safety checks and response normalization for Parva tool wrappers."""

from __future__ import annotations

from typing import Any

from .schemas import TOOL_SPECS, ParvaToolSpec

FORBIDDEN_ROUTE_FRAGMENTS = (
    "future-bs/month-lengths",
    "future-bs/backtest",
    "future-bs/model-runs",
    "future-bs/export",
    "future-bs/loan-impact",
    "calendar-model-risk/prediction",
    "calendar-model-risk/audit-external-sheet",
    "calendar-model-risk/calendar-var",
    "calendar-model-risk/stress-test",
    "/admin/",
    "/billing/",
    "/keys",
    "/webhooks",
    "/trust/mutate",
)

UNSAFE_DESCRIPTION_PHRASES = (
    "official future",
    "government approved",
    "guaranteed future",
    "official future date",
    "legal authority",
    "tax authority",
    "banking authority",
    "payroll authority",
    "payroll approval",
    "government approval",
    "religious authority",
)


def validate_tool_specs(specs: tuple[ParvaToolSpec, ...] = TOOL_SPECS) -> None:
    for spec in specs:
        lowered_route = spec.route.lower()
        lowered_description = spec.description.lower()
        for fragment in FORBIDDEN_ROUTE_FRAGMENTS:
            if fragment in lowered_route:
                raise ValueError(f"{spec.name} exposes forbidden route fragment: {fragment}")
        for phrase in UNSAFE_DESCRIPTION_PHRASES:
            if phrase in lowered_description:
                raise ValueError(f"{spec.name} has unsafe description phrase: {phrase}")
        if not spec.route.startswith("/v3/api/"):
            raise ValueError(f"{spec.name} must use a public-safe v3 route")
        if "claim_boundary" not in spec.output_contract:
            raise ValueError(f"{spec.name} output contract must include claim_boundary")


def normalize_tool_response(payload: Any) -> dict[str, Any]:
    review_required = bool(_find_first(payload, "review_required", default=False))
    publication_status = _find_first(payload, "publication_status", default=None)
    if publication_status == "computed_prediction_not_official":
        review_required = True

    return {
        "answer": payload,
        "source_tier": _find_first(payload, "source_tier", default="public_or_computed"),
        "confidence": _find_first(payload, "confidence", default="unknown"),
        "supported_range": _find_first(payload, "supported_range", default="see_route_metadata"),
        "claim_boundary": _find_first(payload, "claim_boundary", default="decision_support_not_authority"),
        "review_required": review_required,
        "not_authority": (
            "Parva is not an official government, legal, tax, banking, payroll, "
            "future-date, or religious authority."
        ),
    }


def _find_first(value: Any, key: str, *, default: Any) -> Any:
    if isinstance(value, dict):
        if key in value:
            return value[key]
        for child in value.values():
            found = _find_first(child, key, default=None)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_first(child, key, default=None)
            if found is not None:
                return found
    return default
