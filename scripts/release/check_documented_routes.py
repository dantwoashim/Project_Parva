#!/usr/bin/env python3
"""Ensure canonical v3 API routes are represented in route access docs."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.bootstrap.route_introspection import iter_registered_routes  # noqa: E402
from app.main import app  # noqa: E402

API_REFERENCE = PROJECT_ROOT / "docs" / "API_REFERENCE_V3.md"
ROUTE_ACCESS = PROJECT_ROOT / "docs" / "ROUTE_ACCESS.md"
ROUTE_PATTERN = re.compile(r"`(GET|POST|PUT|PATCH|DELETE)\s+([^`\s]+)`")


@dataclass(frozen=True)
class DocumentedRoute:
    method: str
    path: str

    @property
    def canonical_path(self) -> str:
        if self.path.startswith("/v3/api/"):
            return self.path
        if self.path.startswith("/api/"):
            return f"/v3{self.path}"
        return f"/v3/api{self.path}"

    @property
    def request_path(self) -> str:
        return self.canonical_path


def _documented_routes(text: str) -> list[DocumentedRoute]:
    return [
        DocumentedRoute(method=match.group(1), path=match.group(2))
        for match in ROUTE_PATTERN.finditer(text)
    ]


def _canonical_routes() -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for route in iter_registered_routes(app.routes):
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)
        if not isinstance(path, str) or not path.startswith("/v3/api/") or methods is None:
            continue
        for method in methods:
            if method in {"HEAD", "OPTIONS"}:
                continue
            rows.append((method, path))
    return sorted(set(rows), key=lambda row: (row[1], row[0]))


def _route_families(routes: list[tuple[str, str]]) -> set[str]:
    families: set[str] = set()
    for _, path in routes:
        parts = path.removeprefix("/v3/api/").split("/")
        if parts and parts[0]:
            families.add(parts[0])
    return families


def main() -> int:
    failures: list[str] = []
    routes = _canonical_routes()

    if not API_REFERENCE.exists():
        failures.append(f"Missing {API_REFERENCE.relative_to(PROJECT_ROOT)}")
        api_text = ""
    else:
        api_text = API_REFERENCE.read_text(encoding="utf-8")

    if not ROUTE_ACCESS.exists():
        failures.append(f"Missing {ROUTE_ACCESS.relative_to(PROJECT_ROOT)}")
        access_text = ""
    else:
        access_text = ROUTE_ACCESS.read_text(encoding="utf-8")

    for family in sorted(_route_families(routes)):
        if f"/{family}" not in api_text and family not in api_text:
            failures.append(f"API reference does not mention route family: {family}")

    missing_inventory = [
        f"{method} {path}"
        for method, path in routes
        if f"`{method} {path}`" not in access_text
    ]
    if missing_inventory:
        failures.append(
            "ROUTE_ACCESS.md is missing canonical route inventory entries:\n"
            + "\n".join(f"- {item}" for item in missing_inventory[:40])
        )
        if len(missing_inventory) > 40:
            failures.append(f"...and {len(missing_inventory) - 40} more routes.")

    if failures:
        print("\n".join(failures))
        return 1

    print(f"Documented route inventory verified ({len(routes)} canonical v3 routes).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
