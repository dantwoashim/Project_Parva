#!/usr/bin/env python3
"""Verify parity between local in-process API and target HTTP API."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib import parse, request

from fastapi.testclient import TestClient

from app.main import app


def _http_get(base_url: str, endpoint: str, params: dict) -> dict:
    qp = parse.urlencode(params)
    url = f"{base_url.rstrip('/')}{endpoint}"
    if qp:
        url += f"?{qp}"
    with request.urlopen(url, timeout=20) as resp:  # nosec B310
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline parity verifier")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--local-only", action="store_true", help="Compare local in-process API against itself")
    parser.add_argument("--out", default="reports/offline_parity.json")
    args = parser.parse_args()

    cases = [
        ("/v3/api/calendar/convert", {"date": "2026-02-15"}),
        ("/v3/api/calendar/today", {}),
        ("/v3/api/calendar/panchanga", {"date": "2026-02-15"}),
        ("/v3/api/festivals/dashain/explain", {"year": 2026}),
        ("/v3/api/forecast/festivals", {"year": 2040}),
    ]

    client = TestClient(app)
    rows = []
    mismatches = 0
    for endpoint, params in cases:
        local_resp = client.get(endpoint, params=params)
        local_data = local_resp.json() if local_resp.status_code == 200 else {"status": local_resp.status_code}
        if args.local_only:
            remote_data = local_data
            remote_status = local_resp.status_code
        else:
            try:
                remote_data = _http_get(args.base_url, endpoint, params)
                remote_status = 200
            except Exception as exc:
                remote_data = {"error": str(exc)}
                remote_status = 599

        same = local_status_ok(local_resp.status_code, remote_status) and comparable(local_data, remote_data)
        if not same:
            mismatches += 1
        rows.append(
            {
                "endpoint": endpoint,
                "params": params,
                "local_status": local_resp.status_code,
                "remote_status": remote_status,
                "match": same,
            }
        )

    payload = {
        "total_cases": len(cases),
        "mismatches": mismatches,
        "match_rate": round((len(cases) - mismatches) / len(cases), 4),
        "rows": rows,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"Wrote {out}")
    return 0 if mismatches == 0 else 1


def local_status_ok(local_status: int, remote_status: int) -> bool:
    return local_status == remote_status == 200


def comparable(local_data: dict, remote_data: dict) -> bool:
    """
    Compare core shape quickly without requiring perfect dynamic-field equality.
    """
    local_keys = set(local_data.keys())
    remote_keys = set(remote_data.keys())
    # Require at least half of keys to overlap for parity check.
    overlap = len(local_keys & remote_keys)
    denom = max(1, len(local_keys))
    return (overlap / denom) >= 0.5


if __name__ == "__main__":
    raise SystemExit(main())
