#!/usr/bin/env python3
"""Validate that public profiles do not expose Future-BS research-private output."""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
POLICY_PATH = PROJECT_ROOT / "config" / "future-bs-public-policy.yaml"
ROUTE_MATURITY_PATH = PROJECT_ROOT / "config" / "route-maturity.yaml"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

REQUIRED_DOCS = [
    "docs/future_bs/RESEARCH_BOUNDARY.md",
    "docs/future_bs/PUBLIC_CLAIMS_POLICY.md",
    "docs/future_bs/PRIVATE_DATA_POLICY.md",
    "docs/future_bs/ACCURACY_REPRODUCIBILITY.md",
    "docs/future_bs/WRONG_GREEN_POLICY.md",
    "docs/future_bs/MODEL_REGISTRY.md",
    "reports/phase_07_future_bs_governance/module_classification.md",
]
SDK_CODE_GLOBS = [
    "packages/parva-js/src/**/*.ts",
    "packages/parva-python/parva/**/*.py",
]
SDK_PRIVATE_ROUTE_TOKENS = [
    "/v4/api/future-bs/month-lengths",
    "/v4/api/future-bs/backtest",
    "/v4/api/future-bs/model-runs",
    "/v4/api/future-bs/export",
    "/v4/api/future-bs/loan-impact",
    "/v5/api/calendar-model-risk/prediction",
    "/v5/api/calendar-model-risk/audit-external-sheet",
    "/v5/api/calendar-model-risk/calendar-var",
    "/v5/api/calendar-model-risk/stress-test",
]


def _read_json_subset(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _policy() -> dict[str, Any]:
    return _read_json_subset(POLICY_PATH)


def _route_maturity() -> dict[str, Any]:
    return _read_json_subset(ROUTE_MATURITY_PATH)


def _is_private_route(path: str, policy: dict[str, Any]) -> bool:
    allowlist = set(policy["private_route_allowlist"])
    if path in allowlist:
        return False
    return any(path.startswith(prefix) for prefix in policy["private_route_prefixes"])


def _line_allowed_by_context(
    *,
    line_lower: str,
    heading_lower: str,
    policy: dict[str, Any],
) -> bool:
    if any(hint in line_lower for hint in policy["claim_negation_hints"]):
        return True
    return any(token in heading_lower for token in ("disallowed", "forbidden", "not claimed"))


def check_required_files() -> list[str]:
    failures: list[str] = []
    for relative in REQUIRED_DOCS:
        path = PROJECT_ROOT / relative
        if not path.exists():
            failures.append(f"Missing required Phase 07 artifact: {relative}")
            continue
        if not path.read_text(encoding="utf-8").strip():
            failures.append(f"Required Phase 07 artifact is empty: {relative}")
    return failures


def check_route_maturity(policy: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    maturity = _route_maturity()
    public_profiles = set(policy["public_profiles"])
    capability_paths = set(policy["public_capability_paths"])
    for route in maturity.get("routes", []):
        path = str(route.get("path", ""))
        allowed_profiles = set(route.get("allowed_profiles") or [])
        public_overlap = sorted(public_profiles.intersection(allowed_profiles))
        if not public_overlap:
            continue
        if _is_private_route(path, policy):
            failures.append(
                f"Route maturity allows public profile {public_overlap} on private route {path}"
            )
        if path not in capability_paths and route.get("exact_future_output") is True:
            failures.append(f"Public profile {public_overlap} has exact future output on {path}")
        if route.get("private_data") is True:
            failures.append(f"Public profile {public_overlap} has private data on {path}")
        if route.get("research_data") is True:
            failures.append(f"Public profile {public_overlap} has research data on {path}")
        if route.get("public_profile_allowed") is False:
            failures.append(f"Public profile {public_overlap} is disallowed on {path}")
    return failures


def check_openapi_artifacts(policy: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for relative in policy["public_openapi_artifacts"]:
        path = PROJECT_ROOT / relative
        if not path.exists():
            failures.append(f"Missing public OpenAPI artifact: {relative}")
            continue
        spec = json.loads(path.read_text(encoding="utf-8"))
        for api_path in spec.get("paths", {}):
            if _is_private_route(api_path, policy):
                failures.append(f"{relative} exposes private Future-BS route {api_path}")
    return failures


@contextmanager
def _patched_env(values: dict[str, str]) -> Iterator[None]:
    old_values = {key: os.environ.get(key) for key in values}
    os.environ.update(values)
    try:
        yield
    finally:
        for key, value in old_values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _app_for_profile(profile: str, *, experimental: bool, research: bool):
    from app.bootstrap.app_factory import create_app

    with _patched_env(
        {
            "PARVA_ENV": "test",
            "PARVA_ROUTE_PROFILE": profile,
            "PARVA_ENABLE_EXPERIMENTAL_API": "true" if experimental else "false",
            "PARVA_ENABLE_RESEARCH_API": "true" if research else "false",
            "PARVA_SHOW_PRIVATE_SCHEMA": "false",
            "PARVA_ADMIN_TOKEN": "phase07-test-token",
            "PARVA_RATE_LIMIT_ENABLED": "false",
            "PARVA_REQUIRE_PRECOMPUTED": "false",
        }
    ):
        return create_app()


def _route_paths(app: Any) -> set[str]:
    return {
        str(getattr(route, "path", ""))
        for route in app.routes
        if isinstance(getattr(route, "path", None), str)
    }


def check_public_profile_apps(policy: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for profile in policy["public_profiles"]:
        app = _app_for_profile(profile, experimental=False, research=False)
        for path in _route_paths(app):
            if _is_private_route(path, policy):
                failures.append(f"Public profile {profile} mounts private route {path}")
        schema_paths = set(app.openapi().get("paths", {}))
        for path in schema_paths:
            if _is_private_route(path, policy):
                failures.append(f"Public profile {profile} schemas private route {path}")
    return failures


def check_research_route_gates(policy: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    guarded = _app_for_profile("full_dev", experimental=True, research=False)
    guarded_paths = _route_paths(guarded)
    for path in guarded_paths:
        if _is_private_route(path, policy):
            failures.append(f"Private route mounted without PARVA_ENABLE_RESEARCH_API=true: {path}")

    from fastapi.testclient import TestClient

    private_app = _app_for_profile("research_private", experimental=True, research=True)
    private_paths = _route_paths(private_app)
    for required in (
        "/v4/api/future-bs/month-lengths/{bs_year}",
        "/v5/api/calendar-model-risk/prediction/{bs_year}/{month}",
    ):
        if required not in private_paths:
            failures.append(f"Research-private app did not mount expected route: {required}")

    client = TestClient(private_app)
    protected_paths = [
        "/v4/api/future-bs/month-lengths/2085",
        "/v5/api/calendar-model-risk/prediction/2089/6",
    ]
    for path in protected_paths:
        response = client.get(path)
        if response.status_code != 401:
            failures.append(f"Unauthenticated private route {path} returned {response.status_code}")
    return failures


def check_public_text(policy: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    phrases = [phrase.lower() for phrase in policy["forbidden_public_claim_phrases"]]
    heuristic_label = str(policy["heuristic_accuracy_label"]).lower()
    for relative in policy["public_scan_paths"]:
        path = PROJECT_ROOT / relative
        if not path.exists():
            failures.append(f"Configured public scan path is missing: {relative}")
            continue
        heading_lower = ""
        lines = path.read_text(encoding="utf-8").splitlines()
        for line_number, line in enumerate(lines, start=1):
            stripped = line.strip()
            line_lower = stripped.lower()
            if stripped.startswith("#"):
                heading_lower = line_lower
            for phrase in phrases:
                if phrase in line_lower and not _line_allowed_by_context(
                    line_lower=line_lower,
                    heading_lower=heading_lower,
                    policy=policy,
                ):
                    failures.append(f"{relative}:{line_number} has unsafe public claim: {phrase}")
            if "estimated_accuracy" in line_lower and heuristic_label not in line_lower:
                window = " ".join(lines[max(0, line_number - 2) : line_number + 1]).lower()
                if "heuristic" not in window:
                    failures.append(
                        f"{relative}:{line_number} uses estimated_accuracy without heuristic label"
                    )
    return failures


def check_public_sdk_defaults() -> list[str]:
    failures: list[str] = []
    for pattern in SDK_CODE_GLOBS:
        for path in PROJECT_ROOT.glob(pattern):
            if "__pycache__" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            for token in SDK_PRIVATE_ROUTE_TOKENS:
                if token in text:
                    failures.append(
                        f"{path.relative_to(PROJECT_ROOT)} exposes private route token {token}"
                    )
    return failures


def run_checks() -> list[str]:
    policy = _policy()
    failures: list[str] = []
    failures.extend(check_required_files())
    failures.extend(check_route_maturity(policy))
    failures.extend(check_openapi_artifacts(policy))
    failures.extend(check_public_profile_apps(policy))
    failures.extend(check_research_route_gates(policy))
    failures.extend(check_public_text(policy))
    failures.extend(check_public_sdk_defaults())
    return failures


def main() -> int:
    failures = run_checks()
    if failures:
        print("Future-BS public leakage check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(
        json.dumps(
            {
                "ok": True,
                "policy": str(POLICY_PATH.relative_to(PROJECT_ROOT)),
                "checked": [
                    "required_phase07_artifacts",
                    "route_maturity_public_profiles",
                    "public_openapi_artifacts",
                    "public_profile_apps",
                    "research_route_gates",
                    "public_claim_text",
                    "public_sdk_defaults",
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
