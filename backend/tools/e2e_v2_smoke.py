#!/usr/bin/env python3
"""Run end-to-end smoke checks for major v2 endpoints."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_MD = PROJECT_ROOT / "docs" / "weekly_execution" / "year1_week36" / "e2e_smoke.md"


def main() -> None:
    client = TestClient(app)

    checks = [
        ("GET", "/v2/api/calendar/today", None),
        ("GET", "/v2/api/calendar/convert", {"date": "2026-02-15"}),
        ("GET", "/v2/api/calendar/panchanga", {"date": "2026-02-15"}),
        ("GET", "/v2/api/festivals", None),
        ("GET", "/v2/api/festivals/upcoming", {"days": 30}),
        ("GET", "/v2/api/festivals/dashain", {"year": 2026}),
        ("GET", "/v2/api/festivals/dashain/explain", {"year": 2026}),
        ("GET", "/v2/api/temples", None),
        ("GET", "/v2/api/engine/config", None),
    ]

    results = []
    for method, path, params in checks:
        resp = client.request(method, path, params=params)
        ok = resp.status_code == 200
        results.append(
            {
                "method": method,
                "path": path,
                "status": resp.status_code,
                "ok": ok,
            }
        )

    passed = sum(1 for r in results if r["ok"])

    lines = [
        "# V2 E2E Smoke Report",
        "",
        f"- Generated: `{datetime.now(timezone.utc).isoformat()}`",
        f"- Passed: **{passed}/{len(results)}**",
        "",
        "| Method | Path | Status | Result |",
        "|---|---|---:|---|",
    ]

    for row in results:
        lines.append(
            f"| {row['method']} | {row['path']} | {row['status']} | {'PASS' if row['ok'] else 'FAIL'} |"
        )

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({"passed": passed, "total": len(results)}, indent=2))
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
