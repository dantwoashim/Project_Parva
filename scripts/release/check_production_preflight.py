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
    app = create_app()
    settings = app.state.settings
    failures: list[str] = []

    if settings.environment.lower() != "production":
        failures.append("PARVA_ENV must be production for production preflight.")
    if not settings.source_url:
        failures.append("PARVA_SOURCE_URL is required for production preflight.")
    if settings.rate_limit_enabled and settings.rate_limit_backend.lower() != "redis":
        failures.append("Production preflight requires PARVA_RATE_LIMIT_BACKEND=redis.")
    if settings.rate_limit_backend.lower() == "redis" and not settings.redis_url:
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

    unclassified = find_unclassified_api_routes(app.routes)
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
                "source_url": settings.source_url,
                "route_count": len(app.routes),
                "startup_ready": startup_checks.get("ready"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
