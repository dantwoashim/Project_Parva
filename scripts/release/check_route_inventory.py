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


def main() -> int:
    failures: list[str] = []
    all_api_routes = _api_routes()
    canonical_v3_routes = _api_routes("/v3/api/")
    legacy_routes = _api_routes("/api/")

    if len(canonical_v3_routes) < 100:
        failures.append(
            f"Expected a substantial canonical v3 surface; found only {len(canonical_v3_routes)} routes."
        )

    for method, v3_path in sorted(canonical_v3_routes):
        legacy_path = v3_path.removeprefix("/v3")
        if (method, legacy_path) not in legacy_routes:
            failures.append(f"Missing legacy parity route for {method} {v3_path}: {legacy_path}")

    for method, legacy_path in sorted(legacy_routes):
        v3_path = f"/v3{legacy_path}"
        if (method, v3_path) not in canonical_v3_routes:
            failures.append(f"Legacy route lacks canonical v3 equivalent: {method} {legacy_path}")

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
                "canonical_v3_route_count": len(canonical_v3_routes),
                "legacy_route_count": len(legacy_routes),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
