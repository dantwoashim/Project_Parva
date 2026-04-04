#!/usr/bin/env python3
"""Benchmark harness for pack-driven API evaluation (Year-3 prep)."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple
from urllib import parse, request

try:
    from benchmark.validate_pack import validate_pack_file
except ModuleNotFoundError:  # pragma: no cover - direct script execution fallback
    from validate_pack import validate_pack_file  # type: ignore


def _resolve_path(payload: Dict[str, Any], dotted: str) -> Any:
    current: Any = payload
    for part in dotted.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            raise KeyError(dotted)
    return current


def _compare_value(actual: Any, expected: Any, tolerance: float) -> bool:
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return abs(float(actual) - float(expected)) <= tolerance
    return actual == expected


def _http_get_json(base_url: str, endpoint: str, params: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    qp = parse.urlencode({k: v for k, v in params.items() if v is not None})
    url = f"{base_url.rstrip('/')}{endpoint}"
    if qp:
        url = f"{url}?{qp}"
    start = time.perf_counter()
    with request.urlopen(url, timeout=20) as resp:  # nosec B310
        data = json.loads(resp.read().decode("utf-8"))
    elapsed_ms = int((time.perf_counter() - start) * 1000)
    return data, elapsed_ms


def _build_local_requester() -> Callable[[str, Dict[str, Any]], Tuple[Dict[str, Any], int]]:
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    def _request_local(endpoint: str, params: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        start = time.perf_counter()
        resp = client.get(endpoint, params=params)
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        if resp.status_code != 200:
            raise RuntimeError(f"local request failed {resp.status_code}: {resp.text}")
        return resp.json(), elapsed_ms

    return _request_local


def run_pack(
    pack: Dict[str, Any],
    base_url: str,
    requester: Callable[[str, Dict[str, Any]], Tuple[Dict[str, Any], int]] | None = None,
) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    request_fn = requester or (lambda endpoint, params: _http_get_json(base_url, endpoint, params))

    for case in pack["cases"]:
        tolerance = float(case.get("tolerance", 0))
        status = "pass"
        errors: List[str] = []
        observed: Dict[str, Any] = {}

        try:
            response, elapsed_ms = request_fn(case["endpoint"], case.get("params", {}))
        except Exception as exc:
            response = {}
            elapsed_ms = -1
            status = "fail"
            errors.append(f"request_error: {exc}")
            rows.append(
                {
                    "id": case["id"],
                    "status": status,
                    "elapsed_ms": elapsed_ms,
                    "observed": observed,
                    "errors": errors,
                }
            )
            continue

        for dotted, expected in case["assertions"].items():
            try:
                actual = _resolve_path(response, dotted)
                observed[dotted] = actual
            except KeyError:
                status = "fail"
                errors.append(f"missing_path: {dotted}")
                continue

            if not _compare_value(actual, expected, tolerance):
                status = "fail"
                errors.append(f"assertion_failed: {dotted} expected={expected} actual={actual}")

        rows.append(
            {
                "id": case["id"],
                "status": status,
                "elapsed_ms": elapsed_ms,
                "observed": observed,
                "errors": errors,
            }
        )

    total = len(rows)
    passed = sum(1 for r in rows if r["status"] == "pass")
    avg_ms = round(sum(max(0, r["elapsed_ms"]) for r in rows) / total, 2) if total else 0

    return {
        "pack_id": pack["pack_id"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_url": base_url,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round((passed / total * 100), 2) if total else 100.0,
            "avg_latency_ms": avg_ms,
        },
        "results": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run benchmark pack against Parva API")
    parser.add_argument("pack", help="Path to benchmark pack JSON")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--local", action="store_true", help="Run against in-process FastAPI TestClient")
    parser.add_argument("--out", default="", help="Optional output JSON path")
    args = parser.parse_args()

    pack_path = Path(args.pack)
    if not pack_path.exists():
        print(f"Pack not found: {pack_path}")
        return 2

    errors = validate_pack_file(pack_path)
    if errors:
        print("Pack validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    request_fn = _build_local_requester() if args.local else None
    report = run_pack(pack, args.base_url, requester=request_fn)

    out_path = Path(args.out) if args.out else Path("benchmark/results") / f"{pack['pack_id']}_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report["summary"], indent=2))
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
