#!/usr/bin/env python3
"""Run minimal Parva Temporal Spec conformance checks."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402


OUT = PROJECT_ROOT / "reports" / "conformance_report.json"
CASE_PACK = PROJECT_ROOT / "tests" / "conformance" / "conformance_cases.v1.json"


def _check(client: TestClient, endpoint: str, params: dict | None = None, required_keys: list[str] | None = None, case_id: str | None = None):
    resp = client.get(endpoint, params=params or {})
    ok = resp.status_code == 200
    body = resp.json() if ok else {}
    missing = []
    for key in required_keys or []:
        if key not in body:
            missing.append(key)
            ok = False
    return {
        "id": case_id or endpoint,
        "endpoint": endpoint,
        "params": params or {},
        "status": resp.status_code,
        "pass": ok,
        "missing_keys": missing,
    }


def _load_cases() -> list[dict]:
    if CASE_PACK.exists():
        payload = json.loads(CASE_PACK.read_text(encoding="utf-8"))
        return payload.get("cases", [])
    # Fallback legacy static list
    return [
        {
            "id": "calendar-convert-v3",
            "endpoint": "/v3/api/calendar/convert",
            "params": {"date": "2026-02-15"},
            "required_keys": ["bikram_sambat", "tithi", "provenance", "policy"],
        }
    ]


def main() -> int:
    client = TestClient(app)
    checks = []
    for case in _load_cases():
        checks.append(
            _check(
                client,
                case["endpoint"],
                case.get("params"),
                case.get("required_keys"),
                case_id=case.get("id"),
            )
        )
    total = len(checks)
    passed = sum(1 for c in checks if c["pass"])
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": round((passed / total) * 100, 2) if total else 100.0,
        "checks": checks,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"Wrote {OUT}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
