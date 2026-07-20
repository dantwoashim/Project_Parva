"""Curated OpenAPI surfaces for public deployments."""

from __future__ import annotations

import heapq
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Final

from fastapi import FastAPI

HTTP_METHODS: Final[frozenset[str]] = frozenset(
    {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
)


@dataclass(frozen=True)
class CanonicalOperation:
    tag: str
    summary: str


# Insertion order controls the order of operations in the generated schema.
CANONICAL_PUBLIC_OPERATIONS: Final[dict[tuple[str, str], CanonicalOperation]] = {
    ("get", "/health/ready"): CanonicalOperation("Platform", "Check API readiness"),
    ("get", "/v3/api/policy"): CanonicalOperation("Platform", "View the public API policy"),
    ("get", "/v3/api/calendar/today"): CanonicalOperation(
        "Calendar", "Get today's Nepali calendar date"
    ),
    ("get", "/v3/api/calendar/convert"): CanonicalOperation(
        "Calendar", "Convert a Gregorian date to Bikram Sambat"
    ),
    ("post", "/v3/api/calendar/bs-to-gregorian"): CanonicalOperation(
        "Calendar", "Convert a Bikram Sambat date to Gregorian"
    ),
    ("get", "/v3/api/calendar/validate-bs-date"): CanonicalOperation(
        "Calendar", "Validate a Bikram Sambat date"
    ),
    ("get", "/v3/api/calendar/dual-month"): CanonicalOperation(
        "Calendar", "Get a dual-calendar month view"
    ),
    ("get", "/v3/api/calendar/panchanga"): CanonicalOperation(
        "Calendar", "Calculate Panchanga for a date and place"
    ),
    ("get", "/v3/api/festivals"): CanonicalOperation("Festivals", "List supported festivals"),
    ("get", "/v3/api/festivals/upcoming"): CanonicalOperation(
        "Festivals", "Find upcoming festivals"
    ),
    ("get", "/v3/api/festivals/timeline"): CanonicalOperation(
        "Festivals", "Build a festival timeline"
    ),
    ("get", "/v3/api/festivals/on-date/{target_date}"): CanonicalOperation(
        "Festivals", "Find festivals observed on a date"
    ),
    ("get", "/v3/api/festivals/{festival_id}"): CanonicalOperation(
        "Festivals", "Get festival details"
    ),
    ("post", "/v3/api/temporal/compass"): CanonicalOperation(
        "Planning", "Evaluate a date through the temporal compass"
    ),
    ("post", "/v3/api/muhurta/heatmap"): CanonicalOperation(
        "Planning", "Generate a Muhurta heatmap"
    ),
    ("get", "/v3/api/muhurta/calendar"): CanonicalOperation(
        "Planning", "Generate a Muhurta calendar"
    ),
    ("get", "/v3/api/enterprise/fiscal-year/{bs_year}"): CanonicalOperation(
        "Business Rules", "Get Bikram Sambat fiscal-year boundaries"
    ),
    ("get", "/v3/api/enterprise/bs-months/{bs_year}"): CanonicalOperation(
        "Business Rules", "Get published Bikram Sambat month lengths"
    ),
    ("post", "/v3/api/enterprise/business-days"): CanonicalOperation(
        "Business Rules", "Count business days between two dates"
    ),
    ("post", "/v3/api/compliance/evaluate-date"): CanonicalOperation(
        "Business Rules", "Evaluate a date against a compliance profile"
    ),
    ("post", "/v3/api/compliance/add-working-days"): CanonicalOperation(
        "Business Rules", "Add working days to a date"
    ),
    ("get", "/v3/api/feeds/all.ics"): CanonicalOperation(
        "Integrations", "Download the complete festival calendar feed"
    ),
    ("get", "/v3/api/feeds/next"): CanonicalOperation(
        "Integrations", "Get the next calendar event"
    ),
    ("get", "/v4/api/future-bs/capabilities"): CanonicalOperation(
        "Future BS Research", "View future Bikram Sambat research capabilities"
    ),
    ("get", "/v5/api/calendar-model-risk/capabilities"): CanonicalOperation(
        "Future BS Research", "View calendar model-risk capabilities"
    ),
}

CANONICAL_TAGS: Final[list[dict[str, str]]] = [
    {
        "name": "Calendar",
        "description": "BS/AD conversion, validation, month views, and Panchanga.",
    },
    {
        "name": "Festivals",
        "description": "Festival discovery, schedules, and date-based lookup.",
    },
    {
        "name": "Planning",
        "description": "Temporal planning and Muhurta evaluation.",
    },
    {
        "name": "Business Rules",
        "description": "Fiscal periods, month lengths, and working-day rules.",
    },
    {
        "name": "Integrations",
        "description": "Calendar feeds for external applications.",
    },
    {
        "name": "Future BS Research",
        "description": "Capability discovery for explicitly labelled future-calendar research.",
    },
    {
        "name": "Platform",
        "description": "Service health and public access policy.",
    },
]


def _component_refs(value: Any) -> set[tuple[str, str]]:
    refs: set[tuple[str, str]] = set()
    if isinstance(value, dict):
        ref = value.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/components/"):
            parts = ref.split("/", 3)
            if len(parts) == 4:
                refs.add((parts[2], parts[3]))
        for nested in value.values():
            refs.update(_component_refs(nested))
    elif isinstance(value, list):
        for nested in value:
            refs.update(_component_refs(nested))
    return refs


def _drop_explicit_open_object_defaults(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _drop_explicit_open_object_defaults(item)
            for key, item in value.items()
            if not (key == "additionalProperties" and item is True)
        }
    if isinstance(value, list):
        return [_drop_explicit_open_object_defaults(item) for item in value]
    return value


def _reachable_components(
    source_components: dict[str, Any], paths: dict[str, Any]
) -> dict[str, Any]:
    retained: dict[str, dict[str, Any]] = {}
    pending = list(_component_refs(paths))
    heapq.heapify(pending)
    visited: set[tuple[str, str]] = set()

    while pending:
        section, name = heapq.heappop(pending)
        key = (section, name)
        if key in visited:
            continue
        visited.add(key)

        source_section = source_components.get(section)
        if not isinstance(source_section, dict) or name not in source_section:
            continue
        component = deepcopy(source_section[name])
        retained.setdefault(section, {})[name] = component
        for component_ref in _component_refs(component) - visited:
            heapq.heappush(pending, component_ref)

    # Security requirements refer to schemes by name rather than through $ref.
    security_schemes = source_components.get("securitySchemes")
    if isinstance(security_schemes, dict):
        retained["securitySchemes"] = deepcopy(security_schemes)
    return retained


def curate_openapi_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Return a schema containing only the canonical public operations."""
    curated = deepcopy(schema)
    source_paths = schema.get("paths", {})
    curated_paths: dict[str, dict[str, Any]] = {}

    for (method, path), metadata in CANONICAL_PUBLIC_OPERATIONS.items():
        source_path_item = source_paths.get(path)
        if not isinstance(source_path_item, dict):
            continue
        source_operation = source_path_item.get(method)
        if not isinstance(source_operation, dict):
            continue

        target_path_item = curated_paths.setdefault(path, {})
        for key, value in source_path_item.items():
            if key.lower() not in HTTP_METHODS:
                target_path_item[key] = deepcopy(value)

        operation = deepcopy(source_operation)
        operation["tags"] = [metadata.tag]
        operation["summary"] = metadata.summary
        target_path_item[method] = operation

    curated["paths"] = curated_paths
    source_components = schema.get("components")
    if isinstance(source_components, dict):
        curated["components"] = _reachable_components(source_components, curated_paths)
    curated["tags"] = deepcopy(CANONICAL_TAGS)
    curated["x-parva-openapi-surface"] = "canonical"
    normalized = _drop_explicit_open_object_defaults(curated)
    if not isinstance(normalized, dict):  # pragma: no cover - curated is always a mapping.
        raise TypeError("Curated OpenAPI schema must be a mapping")
    return normalized


def install_openapi_surface(app: FastAPI, *, surface: str) -> None:
    """Install the requested OpenAPI view without changing runtime routing."""
    if surface == "full":
        return
    if surface != "canonical":
        raise ValueError(f"Unsupported OpenAPI surface: {surface}")

    generate_full_schema = app.openapi
    app.openapi_schema = None

    def canonical_openapi() -> dict[str, Any]:
        if app.openapi_schema is not None:
            return app.openapi_schema
        full_schema = generate_full_schema()
        app.openapi_schema = curate_openapi_schema(full_schema)
        return app.openapi_schema

    app.openapi = canonical_openapi
