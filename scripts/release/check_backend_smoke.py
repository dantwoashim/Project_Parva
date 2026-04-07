#!/usr/bin/env python3
"""Exercise a small set of canonical backend routes with TestClient."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402


def main() -> int:
    logging.disable(logging.CRITICAL)
    client = TestClient(app)
    checks = [
        ("GET", "/health/live", None),
        ("GET", "/health/ready", None),
        ("GET", "/v3/api/calendar/today", None),
        ("GET", "/v3/api/festivals/upcoming?days=14&quality_band=computed", None),
        ("GET", "/v3/api/policy", None),
        (
            "POST",
            "/v3/api/personal/panchanga",
            {"date": "2026-02-15", "lat": "27.7172", "lon": "85.3240", "tz": "Asia/Kathmandu"},
        ),
        (
            "POST",
            "/v3/api/muhurta/heatmap",
            {"date": "2026-02-15", "lat": "27.7172", "lon": "85.3240", "tz": "Asia/Kathmandu"},
        ),
        (
            "POST",
            "/v3/api/kundali/graph",
            {"datetime": "2026-02-15T06:30:00+05:45", "lat": "27.7172", "lon": "85.3240", "tz": "Asia/Kathmandu"},
        ),
    ]

    report: list[dict[str, object]] = []
    failed = False

    for method, path, payload in checks:
        if method == "GET":
            response = client.get(path)
        else:
            response = client.post(path, json=payload)

        ok = response.status_code == 200
        failed = failed or not ok
        try:
            body = response.json()
            keys = sorted(body.keys())[:8] if isinstance(body, dict) else []
        except ValueError:
            keys = []

        report.append(
            {
                "method": method,
                "path": path,
                "status": response.status_code,
                "ok": ok,
                "keys": keys,
            }
        )

    print(json.dumps({"ok": not failed, "checks": report}, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
