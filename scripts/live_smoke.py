#!/usr/bin/env python3
"""Run smoke checks against a live/base URL.

Example:
  python3 scripts/live_smoke.py --base http://localhost:8000
"""

from __future__ import annotations

import argparse
import json
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def fetch(url: str) -> tuple[int, str]:
    req = Request(url, headers={"Accept": "application/json"})
    with urlopen(req, timeout=20) as resp:
        body = resp.read().decode("utf-8")
        return resp.status, body


def main() -> int:
    parser = argparse.ArgumentParser(description="Parva live smoke checks")
    parser.add_argument("--base", default="http://localhost:8000", help="Base host")
    args = parser.parse_args()

    base = args.base.rstrip("/")
    checks = [
        ("/health", {}),
        ("/v3/api/calendar/today", {}),
        ("/v3/api/calendar/convert", {"date": "2026-02-15"}),
        ("/v3/api/calendar/panchanga", {"date": "2026-02-15"}),
        ("/v3/api/festivals/dashain", {"year": "2026"}),
        ("/v3/api/festivals/dashain/explain", {"year": "2026"}),
        ("/v3/api/reliability/status", {}),
        ("/v3/api/personal/panchanga", {"date": "2026-02-15"}),
        ("/v3/api/muhurta", {"date": "2026-02-15"}),
        ("/v3/api/kundali", {"datetime": "2026-02-15T06:30:00+05:45"}),
    ]

    report = []
    all_ok = True

    for path, params in checks:
        query = f"?{urlencode(params)}" if params else ""
        url = f"{base}{path}{query}"
        try:
            status, body = fetch(url)
            payload = json.loads(body)
            ok = status == 200
            report.append({"path": path, "status": status, "ok": ok, "keys": list(payload.keys())[:8]})
            all_ok = all_ok and ok
        except Exception as exc:
            report.append({"path": path, "status": "error", "ok": False, "error": str(exc)})
            all_ok = False

    print(json.dumps({"base": base, "all_ok": all_ok, "checks": report}, indent=2))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
