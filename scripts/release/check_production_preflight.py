#!/usr/bin/env python3
"""Validate that a production-like environment satisfies Parva's minimum runtime rules."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.bootstrap.app_factory import create_app  # noqa: E402


def main() -> int:
    try:
        app = create_app()
    except Exception as exc:
        print(f"[production-preflight] failed: {exc}")
        return 1

    settings = app.state.settings
    startup_checks = app.state.startup_checks
    summary = {
        "environment": settings.environment,
        "source_url": settings.source_url,
        "rate_limit_backend": settings.rate_limit_backend,
        "require_precomputed": settings.require_precomputed,
        "place_search": {
            "policy": settings.place_search_provider_policy,
            "allow_remote": settings.place_search_allow_remote,
            "provider_chain": list(settings.place_search_provider_chain),
            "endpoint": settings.place_search_endpoint,
        },
        "startup_ready": startup_checks["ready"],
        "checks": startup_checks["checks"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
