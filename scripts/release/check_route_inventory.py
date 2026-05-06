#!/usr/bin/env python3
"""Validate API route registration, classification, and v3 legacy parity."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.bootstrap.access_control import find_unclassified_api_routes  # noqa: E402
from app.main import app  # noqa: E402


def _api_routes(prefix: str | None = None) -> dict[tuple[str, str], str]:
    routes: dict[tuple[str, str], str] = {}
    for route in app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)
        name = str(getattr(route, "name", "") or "")
        if not isinstance(path, str) or methods is None:
            continue
        if prefix and not path.startswith(prefix):
            continue
        for method in methods:
            if method in {"HEAD", "OPTIONS"}:
                continue
            routes[(method, path)] = name
    return routes


def _build_inventory() -> dict:
    canonical_prefix = "/v3/api"
    compat_prefix = "/api"
    canonical_v3_routes = _api_routes(f"{canonical_prefix}/")
    legacy_routes = _api_routes(f"{compat_prefix}/")
    alias_gaps: list[str] = []

    for method, v3_path in sorted(canonical_v3_routes):
        legacy_path = v3_path.removeprefix("/v3")
        if (method, legacy_path) not in legacy_routes:
            alias_gaps.append(f"Missing legacy parity route for {method} {v3_path}: {legacy_path}")

    for method, legacy_path in sorted(legacy_routes):
        v3_path = f"/v3{legacy_path}"
        if (method, v3_path) not in canonical_v3_routes:
            alias_gaps.append(f"Legacy route lacks canonical v3 equivalent: {method} {legacy_path}")

    return {
        "canonical_prefix": canonical_prefix,
        "compat_prefix": compat_prefix,
        "v3_count": len(canonical_v3_routes),
        "compat_count": len(legacy_routes),
        "alias_gaps": alias_gaps,
    }


def main() -> int:
    failures: list[str] = []
    all_api_routes = _api_routes()
    inventory = _build_inventory()

    if inventory["v3_count"] < 100:
        failures.append(
            f"Expected a substantial canonical v3 surface; found only {inventory['v3_count']} routes."
        )
    failures.extend(inventory["alias_gaps"])

    unclassified = find_unclassified_api_routes(app.routes)
    failures.extend(f"Unclassified API route: {route}" for route in unclassified)

    if failures:
        print("\n".join(failures))
        return 1

    print(
        json.dumps(
            {
                "ok": True,
                "route_count": len(all_api_routes),
                "canonical_v3_route_count": inventory["v3_count"],
                "legacy_route_count": inventory["compat_count"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
