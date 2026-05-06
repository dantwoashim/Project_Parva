#!/usr/bin/env python3
"""Validate that the configured production profile can build a safe app."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.bootstrap.access_control import find_unclassified_api_routes  # noqa: E402
from app.bootstrap.app_factory import create_app  # noqa: E402


def main() -> int:
    try:
        app = create_app()
    except Exception as exc:
        print(str(exc))
        return 1
    settings = app.state.settings
    failures: list[str] = []
    rate_limit_enabled = bool(getattr(settings, "rate_limit_enabled", True))
    rate_limit_backend = str(getattr(settings, "rate_limit_backend", "")).lower()

    if settings.environment.lower() != "production":
        failures.append("PARVA_ENV must be production for production preflight.")
    if not settings.source_url:
        failures.append("PARVA_SOURCE_URL is required for production preflight.")
    if rate_limit_enabled and rate_limit_backend != "redis":
        failures.append("Production preflight requires PARVA_RATE_LIMIT_BACKEND=redis.")
    if rate_limit_enabled and rate_limit_backend == "redis" and hasattr(settings, "redis_url") and not settings.redis_url:
        failures.append("Production preflight requires PARVA_REDIS_URL when Redis rate limiting is selected.")

    startup_checks = getattr(app.state, "startup_checks", {})
    if not startup_checks.get("ready"):
        checks = startup_checks.get("checks", {})
        failed_required = [
            name
            for name, detail in checks.items()
            if isinstance(detail, dict) and detail.get("required") and not detail.get("ok")
        ]
        failures.append(f"Required startup checks are not ready: {', '.join(failed_required)}")

    routes = getattr(app, "routes", [])
    unclassified = find_unclassified_api_routes(routes)
    failures.extend(f"Unclassified API route: {route}" for route in unclassified)

    if failures:
        print("\n".join(failures))
        return 1

    print(
        json.dumps(
            {
                "ok": True,
                "environment": settings.environment,
                "rate_limit_backend": settings.rate_limit_backend,
                "policy": getattr(settings, "place_search_provider_policy", None),
                "source_url": settings.source_url,
                "route_count": len(routes),
                "startup_ready": startup_checks.get("ready"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
