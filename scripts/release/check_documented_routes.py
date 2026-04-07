#!/usr/bin/env python3
"""Verify that documented v3 API routes still exist and resolve at runtime."""

from __future__ import annotations

import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402

DOC_PATH = PROJECT_ROOT / "docs" / "API_REFERENCE_V3.md"
ROUTE_PATTERN = re.compile(r"^- `(?P<method>[A-Z]+) (?P<path>/[^`]+)`$")
CANONICAL_API_PREFIX = "/v3/api"


@dataclass(frozen=True)
class DocumentedRoute:
    method: str
    path: str

    @property
    def canonical_path(self) -> str:
        base_path, _, _query = self.path.partition("?")
        if base_path.startswith(("/v3/", "/api/", "/health", "/docs", "/openapi.json", "/source")):
            return base_path
        return f"{CANONICAL_API_PREFIX}{base_path}"

    @property
    def request_path(self) -> str:
        base_path, separator, query = self.path.partition("?")
        if base_path.startswith(("/v3/", "/api/", "/health", "/docs", "/openapi.json", "/source")):
            canonical_base = base_path
        else:
            canonical_base = f"{CANONICAL_API_PREFIX}{base_path}"
        return f"{canonical_base}{separator}{query}" if separator else canonical_base


def _documented_routes(text: str) -> list[DocumentedRoute]:
    routes: list[DocumentedRoute] = []
    for raw_line in text.splitlines():
        match = ROUTE_PATTERN.match(raw_line.strip())
        if not match:
            continue
        routes.append(DocumentedRoute(method=match.group("method"), path=match.group("path")))
    return routes


def _validate_documented_routes(routes: list[DocumentedRoute]) -> list[str]:
    failures: list[str] = []
    schema = app.openapi()
    documented_paths = schema.get("paths", {})
    logging.disable(logging.CRITICAL)
    client = TestClient(app)

    for route in routes:
        methods = {
            candidate.upper()
            for candidate in documented_paths.get(route.canonical_path, {}).keys()
        }
        if route.method not in methods:
            failures.append(
                f"documented route missing from OpenAPI: {route.method} {route.request_path}"
            )
            continue

        if "{" in route.canonical_path:
            continue

        response = client.request(route.method, route.request_path)
        if response.status_code in {404, 405}:
            failures.append(
                f"documented route does not resolve at runtime: {route.method} {route.request_path} -> {response.status_code}"
            )

    return failures


def main() -> int:
    routes = _documented_routes(DOC_PATH.read_text(encoding="utf-8"))
    failures = _validate_documented_routes(routes)
    if failures:
        for failure in failures:
            print(f"[documented-routes] {failure}")
        return 1

    print("[documented-routes] documented route check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
