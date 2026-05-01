#!/usr/bin/env python3
"""Run fast in-process smoke checks against the backend API surface."""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("PARVA_ENV", "test")
os.environ.setdefault("PARVA_RATE_LIMIT_ENABLED", "false")
os.environ.setdefault("PARVA_PLACE_SEARCH_ALLOW_REMOTE", "false")

from app.main import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


def _assert_ok(client: TestClient, method: str, path: str, **kwargs) -> None:
    response = client.request(method, path, **kwargs)
    if response.status_code != 200:
        raise AssertionError(
            f"{method} {path} returned {response.status_code}: {response.text[:500]}"
        )


def main() -> int:
    with TestClient(app) as client:
        _assert_ok(client, "GET", "/health")
        _assert_ok(client, "GET", "/health/ready")
        _assert_ok(client, "GET", "/v3/api/calendar/today")
        _assert_ok(client, "GET", "/v3/api/calendar/convert?date=2026-10-21")
        _assert_ok(client, "GET", "/v3/api/festivals/upcoming?days=30")
        _assert_ok(client, "GET", "/v3/api/policy")
        _assert_ok(
            client,
            "POST",
            "/v3/api/personal/panchanga",
            json={"date": "2026-02-15", "lat": 27.7172, "lon": 85.324, "tz": "Asia/Kathmandu"},
        )

    print("Backend smoke checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
