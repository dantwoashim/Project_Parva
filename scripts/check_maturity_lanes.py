#!/usr/bin/env python3
"""Validate maturity lanes, route profiles, and public exposure rules."""

from __future__ import annotations

import json
import os
import sys
from contextlib import contextmanager
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

SUBSYSTEM_REGISTRY = PROJECT_ROOT / "config" / "subsystem-maturity.yaml"
ROUTE_REGISTRY = PROJECT_ROOT / "config" / "route-maturity.yaml"
PROFILE_OPENAPI_ARTIFACTS = {
    "public_reference": PROJECT_ROOT / "docs" / "api-docs" / "openapi.public-reference.json",
    "developer_preview": PROJECT_ROOT / "docs" / "api-docs" / "openapi.developer-preview.json",
    "enterprise_preview": PROJECT_ROOT / "docs" / "api-docs" / "openapi.enterprise-preview.json",
}
PRIVATE_ROUTE_PREFIXES = (
    "/v4/api/future-bs/",
    "/v5/api/calendar-model-risk/",
)
SAFE_PUBLIC_RESEARCH_CAPABILITIES = {
    "/v4/api/future-bs/capabilities",
    "/v5/api/calendar-model-risk/capabilities",
}
MUTATING_METHODS = {"DELETE", "PATCH", "POST", "PUT"}
AUTH_REQUIRED_VALUES = {"admin", "admin_for_mutation", "operator_controlled", "required"}
PUBLIC_RESPONSE_METADATA_FIELDS = {"claim_boundary", "confidence", "maturity", "release_id", "warnings"}
SIDE_EFFECT_PATH_MARKERS = ("/admin/", "/billing", "/keys", "/me/", "/provenance/", "/webhooks")


def _load_json_registry(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise AssertionError(f"Missing registry: {path.relative_to(PROJECT_ROOT)}") from None
    except json.JSONDecodeError as exc:
        raise AssertionError(f"Registry is not valid JSON-subset YAML: {path}: {exc}") from None


def _relative(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _ensure_docs_exist(entries: list[str], *, owner: str, failures: list[str]) -> None:
    for raw_doc in entries:
        doc = PROJECT_ROOT / raw_doc
        if not doc.exists():
            failures.append(f"{owner} references missing doc: {raw_doc}")
        elif doc.is_file() and doc.stat().st_size == 0:
            failures.append(f"{owner} references empty doc: {raw_doc}")


def _assert_registry_shape(
    subsystem_registry: dict[str, Any], route_registry: dict[str, Any], failures: list[str]
) -> None:
    subsystem_lanes = subsystem_registry.get("lanes", {})
    route_profiles = route_registry.get("profiles", {})
    route_lanes = {entry.get("lane") for entry in route_registry.get("routes", [])}

    if not subsystem_lanes:
        failures.append("Subsystem registry has no lanes.")
    if not subsystem_registry.get("subsystems"):
        failures.append("Subsystem registry has no subsystems.")
    if not route_profiles:
        failures.append("Route registry has no profiles.")
    if not route_registry.get("routes"):
        failures.append("Route registry has no routes.")

    missing_subsystems = sorted(
        set(subsystem_registry.get("required_subsystem_ids", []))
        - set(subsystem_registry.get("subsystems", {}))
    )
    for subsystem_id in missing_subsystems:
        failures.append(f"Required subsystem is missing from registry: {subsystem_id}")

    for subsystem_id, subsystem in subsystem_registry.get("subsystems", {}).items():
        lane = subsystem.get("lane")
        if lane not in subsystem_lanes:
            failures.append(f"Subsystem {subsystem_id} uses unknown lane: {lane}")
        for required_key in (
            "maturity",
            "public_exposure",
            "canonical_runtime",
            "route_profiles",
            "ci_gates",
            "docs",
            "allowed_claims",
            "forbidden_claims",
        ):
            if required_key not in subsystem:
                failures.append(f"Subsystem {subsystem_id} missing key: {required_key}")
        _ensure_docs_exist(
            list(subsystem.get("docs", [])), owner=f"Subsystem {subsystem_id}", failures=failures
        )

    for route in route_registry.get("routes", []):
        path = route.get("path", "<missing>")
        if not isinstance(path, str) or not path.startswith("/"):
            failures.append(f"Route entry has invalid path: {path}")
        if route.get("lane") not in subsystem_lanes:
            failures.append(f"Route {path} uses unknown lane: {route.get('lane')}")
        if route.get("lane") not in route_lanes:
            failures.append(f"Route {path} lane is not represented in route registry: {route.get('lane')}")
        for required_key in (
            "maturity",
            "allowed_profiles",
            "auth",
            "private_data",
            "research_data",
            "exact_future_output",
            "official_authority_risk",
            "cpu_heavy",
            "mutating_side_effects",
            "docs",
        ):
            if required_key not in route:
                failures.append(f"Route {path} missing key: {required_key}")
        if "response_metadata" not in route and "response_metadata_exemption" not in route:
            failures.append(f"Route {path} lacks response metadata or an explicit exemption.")
        if route.get("deprecated") and not route.get("sunset_doc"):
            failures.append(f"Deprecated route {path} lacks sunset_doc.")
        _ensure_docs_exist(list(route.get("docs", [])), owner=f"Route {path}", failures=failures)
        if route.get("sunset_doc"):
            _ensure_docs_exist([route["sunset_doc"]], owner=f"Route {path}", failures=failures)
        if route.get("draft_doc"):
            _ensure_docs_exist([route["draft_doc"]], owner=f"Route {path}", failures=failures)


def _path_specificity(pattern: str) -> tuple[int, int]:
    return (len(pattern.replace("*", "")), len(pattern))


def _match_route(path: str, route_entries: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidate_paths = [path, path.rstrip("/")]
    if path.startswith(("/v2/api/", "/v4/api/", "/v5/api/")) and not path.startswith(
        ("/v4/api/future-bs/", "/v5/api/calendar-model-risk/")
    ):
        candidate_paths.append(f"/v3/api/{path.split('/api/', 1)[1]}")
    if path in {"/v2/openapi.json", "/v4/openapi.json", "/v5/openapi.json"}:
        candidate_paths.append("/v3/openapi.json")

    matches = []
    for entry in route_entries:
        pattern = entry["path"]
        base_pattern = pattern[:-2] if pattern.endswith("/*") else None
        if any(
            fnmatchcase(candidate, pattern)
            or (base_pattern is not None and candidate.rstrip("/") == base_pattern)
            for candidate in candidate_paths
        ):
            matches.append(entry)
    if not matches:
        return None
    return sorted(matches, key=lambda entry: _path_specificity(entry["path"]), reverse=True)[0]


@contextmanager
def _patched_env(values: dict[str, str]):
    old_values = {key: os.environ.get(key) for key in values}
    try:
        os.environ.update(values)
        yield
    finally:
        for key, old_value in old_values.items():
            if old_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value


def _profile_env(profile: str, *, allow_research: bool) -> dict[str, str]:
    return {
        "PARVA_ENV": "test",
        "PARVA_ROUTE_PROFILE": profile,
        "PARVA_ENABLE_EXPERIMENTAL_API": "true" if allow_research else "false",
        "PARVA_SHOW_PRIVATE_SCHEMA": "true" if allow_research else "false",
        "PARVA_ADMIN_TOKEN": "parva-test-admin-token",
        "PARVA_API_KEYS": "local-read:parva-test-read-key:commercial.read|public.read",
        "PARVA_RATE_LIMIT_ENABLED": "false",
        "PARVA_REQUIRE_PRECOMPUTED": "false",
        "PARVA_SERVE_FRONTEND": "false",
        "PARVA_SOURCE_URL": "https://github.com/dantwoashim/Project_Parva",
    }


def _registered_api_routes(profile: str, *, allow_research: bool) -> list[tuple[str, str]]:
    with _patched_env(_profile_env(profile, allow_research=allow_research)):
        from app.bootstrap.app_factory import create_app

        app = create_app()
    routes: set[tuple[str, str]] = set()
    for route in app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)
        if not isinstance(path, str) or methods is None:
            continue
        if not (
            path == "/"
            or path.startswith("/health")
            or path.endswith("/openapi.json")
            or path.startswith("/api/")
            or path.startswith("/v3/api/")
            or path.startswith("/v4/api/")
            or path.startswith("/v5/api/")
        ):
            continue
        for method in methods:
            if method in {"HEAD", "OPTIONS"}:
                continue
            routes.add((method, path))
    return sorted(routes)


def _check_profile_routes(route_registry: dict[str, Any], failures: list[str]) -> dict[str, Any]:
    route_entries = route_registry["routes"]
    profile_results: dict[str, Any] = {}
    public_profiles = set(route_registry.get("public_profiles", []))

    for profile, profile_config in route_registry.get("profiles", {}).items():
        allow_research = bool(profile_config.get("allow_research_private"))
        routes = _registered_api_routes(profile, allow_research=allow_research)
        profile_results[profile] = {"route_count": len(routes), "allow_research_private": allow_research}
        for method, path in routes:
            route_entry = _match_route(path, route_entries)
            if route_entry is None:
                failures.append(f"{profile} registers undocumented route: {method} {path}")
                continue

            allowed_profiles = set(route_entry.get("allowed_profiles", []))
            if profile not in allowed_profiles:
                failures.append(
                    f"{profile} registers {method} {path}, but route registry only allows "
                    f"{sorted(allowed_profiles)}"
                )

            if (
                method in MUTATING_METHODS
                and route_entry.get("mutating_side_effects") not in {False, "matches_v3_family"}
                and (
                    route_entry.get("private_data") is True
                    or route_entry.get("lane") in {"enterprise_preview", "research_private"}
                    or any(marker in path for marker in SIDE_EFFECT_PATH_MARKERS)
                )
            ):
                auth = route_entry.get("auth")
                if auth not in AUTH_REQUIRED_VALUES and auth != "optional":
                    failures.append(f"Mutating route {method} {path} has weak auth classification: {auth}")

            metadata = set(route_entry.get("response_metadata", []))
            if (
                profile in public_profiles
                and "response_metadata_exemption" not in route_entry
                and not (metadata & PUBLIC_RESPONSE_METADATA_FIELDS)
            ):
                failures.append(f"Public route {method} {path} has insufficient metadata fields.")

            is_private_research = (
                route_entry.get("lane") == "research_private"
                or route_entry.get("private_data") is True
                or route_entry.get("research_data") is True
                or route_entry.get("public_profile_allowed") is False
            )
            if not allow_research and is_private_research:
                failures.append(f"{profile} exposes private/research route: {method} {path}")

            if (
                profile in public_profiles
                and route_entry.get("exact_future_output") is True
                and path not in SAFE_PUBLIC_RESEARCH_CAPABILITIES
            ):
                failures.append(f"Public profile {profile} exposes exact future output route: {method} {path}")

    return profile_results


def _check_openapi_artifacts(route_registry: dict[str, Any], failures: list[str]) -> dict[str, Any]:
    artifact_results: dict[str, Any] = {}
    for profile, path in PROFILE_OPENAPI_ARTIFACTS.items():
        if not path.exists():
            failures.append(f"Missing profile OpenAPI artifact for {profile}: {_relative(path)}")
            continue
        if path.stat().st_size == 0:
            failures.append(f"Empty profile OpenAPI artifact for {profile}: {_relative(path)}")
            continue
        try:
            spec = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Invalid JSON in profile OpenAPI artifact {profile}: {exc}")
            continue
        paths = sorted(spec.get("paths", {}))
        artifact_results[profile] = {"path_count": len(paths), "file": _relative(path)}
        for api_path in paths:
            if any(
                api_path.startswith(prefix) and api_path not in SAFE_PUBLIC_RESEARCH_CAPABILITIES
                for prefix in PRIVATE_ROUTE_PREFIXES
            ):
                failures.append(f"{profile} OpenAPI exposes private/research path: {api_path}")
            route_entry = _match_route(api_path, route_registry["routes"])
            if route_entry and route_entry.get("public_profile_allowed") is False:
                failures.append(f"{profile} OpenAPI exposes forbidden route registry path: {api_path}")
    return artifact_results


def main() -> int:
    failures: list[str] = []
    subsystem_registry = _load_json_registry(SUBSYSTEM_REGISTRY)
    route_registry = _load_json_registry(ROUTE_REGISTRY)

    _assert_registry_shape(subsystem_registry, route_registry, failures)
    profile_results: dict[str, Any] = {}
    artifact_results: dict[str, Any] = {}
    if not failures:
        profile_results = _check_profile_routes(route_registry, failures)
        artifact_results = _check_openapi_artifacts(route_registry, failures)

    if failures:
        print("\n".join(failures))
        return 1

    print(
        json.dumps(
            {
                "ok": True,
                "subsystem_count": len(subsystem_registry.get("subsystems", {})),
                "route_entry_count": len(route_registry.get("routes", [])),
                "profiles": profile_results,
                "openapi_artifacts": artifact_results,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
