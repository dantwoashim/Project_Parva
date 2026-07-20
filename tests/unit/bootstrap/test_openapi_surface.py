"""Tests for the curated public OpenAPI surface."""

from __future__ import annotations

from app.bootstrap.app_factory import create_app
from app.bootstrap.openapi_surface import (
    CANONICAL_PUBLIC_OPERATIONS,
    CANONICAL_TAGS,
    curate_openapi_schema,
)
from app.bootstrap.settings import load_settings, validate_settings
from fastapi import FastAPI
from fastapi.testclient import TestClient


def _configure_canonical_app(monkeypatch) -> FastAPI:
    monkeypatch.setenv("PARVA_ENV", "test")
    monkeypatch.setenv("PARVA_EXPOSURE", "local")
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "developer_preview")
    monkeypatch.setenv("PARVA_OPENAPI_SURFACE", "canonical")
    monkeypatch.setenv("PARVA_RATE_LIMIT_ENABLED", "false")
    monkeypatch.setenv("PARVA_REQUIRE_PRECOMPUTED", "false")
    monkeypatch.setenv("PARVA_PREWARM_HOTSET", "false")
    monkeypatch.setenv("PARVA_SERVE_FRONTEND", "false")
    return create_app()


def _operation_keys(schema: dict) -> set[tuple[str, str]]:
    methods = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
    return {
        (method.lower(), path)
        for path, path_item in schema["paths"].items()
        for method in path_item
        if method.lower() in methods
    }


def _schema_refs(value) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        if isinstance(value.get("$ref"), str):
            refs.add(value["$ref"])
        for nested in value.values():
            refs.update(_schema_refs(nested))
    elif isinstance(value, list):
        for nested in value:
            refs.update(_schema_refs(nested))
    return refs


def test_curate_openapi_schema_keeps_only_declared_operations() -> None:
    schema = {
        "openapi": "3.1.0",
        "paths": {
            "/health/ready": {
                "get": {"summary": "Old summary", "tags": ["old"]},
                "parameters": [{"name": "trace", "in": "query"}],
            },
            "/api/internal": {"get": {"summary": "Internal"}},
        },
        "components": {"schemas": {"Health": {"type": "object"}}},
    }

    curated = curate_openapi_schema(schema)

    assert set(curated["paths"]) == {"/health/ready"}
    assert curated["paths"]["/health/ready"]["get"]["summary"] == "Check API readiness"
    assert curated["paths"]["/health/ready"]["get"]["tags"] == ["Platform"]
    assert "parameters" in curated["paths"]["/health/ready"]
    assert curated["components"] == {}
    assert curated["x-parva-openapi-surface"] == "canonical"


def test_curate_openapi_schema_keeps_only_reachable_components() -> None:
    schema = {
        "paths": {
            "/health/ready": {
                "get": {
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Health"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "Health": {
                    "type": "object",
                    "properties": {"status": {"$ref": "#/components/schemas/HealthStatus"}},
                },
                "HealthStatus": {"type": "string"},
                "UnusedInternalModel": {"type": "object"},
            }
        },
    }

    curated = curate_openapi_schema(schema)

    assert set(curated["components"]["schemas"]) == {"Health", "HealthStatus"}


def test_curate_openapi_schema_normalizes_open_object_defaults() -> None:
    schema = {
        "paths": {
            "/health/ready": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "Ready",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "additionalProperties": True,
                                    }
                                }
                            },
                        },
                        "503": {
                            "description": "Invalid extension shape",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "additionalProperties": False,
                                    }
                                }
                            },
                        },
                    }
                }
            }
        }
    }

    curated = curate_openapi_schema(schema)
    responses = curated["paths"]["/health/ready"]["get"]["responses"]

    assert "additionalProperties" not in responses["200"]["content"]["application/json"]["schema"]
    assert (
        responses["503"]["content"]["application/json"]["schema"]["additionalProperties"] is False
    )


def test_canonical_app_exposes_the_intended_documented_contract(monkeypatch) -> None:
    app = _configure_canonical_app(monkeypatch)
    schema = app.openapi()

    assert _operation_keys(schema) == set(CANONICAL_PUBLIC_OPERATIONS)
    assert len(_operation_keys(schema)) == 25
    assert [tag["name"] for tag in schema["tags"]] == [tag["name"] for tag in CANONICAL_TAGS]
    assert not any(path.startswith("/api/") for path in schema["paths"])
    assert "/v3/api/provenance/root" not in schema["paths"]
    assert "/v3/openapi.json" not in schema["paths"]


def test_canonical_app_has_no_dangling_or_orphaned_schemas(monkeypatch) -> None:
    schema = _configure_canonical_app(monkeypatch).openapi()
    schema_names = set(schema["components"]["schemas"])
    referenced_names = {
        ref.removeprefix("#/components/schemas/")
        for ref in _schema_refs(schema["paths"])
        if ref.startswith("#/components/schemas/")
    }
    pending = list(referenced_names)

    while pending:
        name = pending.pop()
        component_refs = {
            ref.removeprefix("#/components/schemas/")
            for ref in _schema_refs(schema["components"]["schemas"][name])
            if ref.startswith("#/components/schemas/")
        }
        unseen = component_refs - referenced_names
        referenced_names.update(unseen)
        pending.extend(unseen)

    assert referenced_names == schema_names


def test_hidden_compatibility_routes_remain_callable(monkeypatch) -> None:
    app = _configure_canonical_app(monkeypatch)

    with TestClient(app) as client:
        response = client.get("/api/calendar/convert", params={"date": "2025-07-16"})

    assert response.status_code == 200
    assert "/api/calendar/convert" not in app.openapi()["paths"]


def test_openapi_surface_setting_is_validated(monkeypatch) -> None:
    monkeypatch.setenv("PARVA_OPENAPI_SURFACE", "everything")

    settings = load_settings()

    assert any("PARVA_OPENAPI_SURFACE" in error for error in validate_settings(settings))
