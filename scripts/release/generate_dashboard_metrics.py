#!/usr/bin/env python3
"""Generate release dashboard metrics for request health and provenance verification."""

from __future__ import annotations

import json
import math
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402
from app.provenance.snapshot import get_latest_snapshot, verify_snapshot  # noqa: E402
from app.provenance.transparency import verify_log_integrity  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

DOCS_DIR = PROJECT_ROOT / "docs" / "public_beta"
OUT_JSON = DOCS_DIR / "dashboard_metrics.json"
OUT_MD = DOCS_DIR / "dashboard_metrics.md"
AUTHORITY_DASHBOARD = PROJECT_ROOT / "reports" / "authority_dashboard.json"

LATENCY_BUDGET_MS = 1000.0
AVAILABILITY_BUDGET_PCT = 99.0


class ArtifactError(RuntimeError):
    """Raised when dashboard metrics cannot be generated."""


ENDPOINT_SPECS: tuple[dict[str, Any], ...] = (
    {"id": "health_ready", "method": "get", "path": "/health/ready"},
    {"id": "calendar_today", "method": "get", "path": "/v3/api/calendar/today"},
    {
        "id": "festivals_timeline",
        "method": "get",
        "path": "/v3/api/festivals/timeline?from=2026-02-15&to=2026-08-15&quality_band=computed&lang=en",
    },
    {
        "id": "personal_panchanga",
        "method": "post",
        "path": "/v3/api/personal/panchanga",
        "json": {"date": "2026-02-15", "lat": 27.7172, "lon": 85.324, "tz": "Asia/Kathmandu"},
    },
    {
        "id": "muhurta_heatmap",
        "method": "post",
        "path": "/v3/api/muhurta/heatmap",
        "json": {
            "date": "2026-02-15",
            "lat": 27.7172,
            "lon": 85.324,
            "tz": "Asia/Kathmandu",
            "type": "general",
            "assumption_set": "np-mainstream-v2",
        },
    },
    {
        "id": "kundali",
        "method": "post",
        "path": "/v3/api/kundali",
        "json": {
            "datetime": "2026-02-15T06:30:00+05:45",
            "lat": 27.7172,
            "lon": 85.324,
            "tz": "Asia/Kathmandu",
        },
    },
)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _round(value: float) -> float:
    return round(value, 2)


def _percent(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return _round((numerator / denominator) * 100.0)


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(len(ordered) * 0.95) - 1))
    return _round(ordered[index])


def _extract_meta(payload: dict[str, Any]) -> dict[str, Any]:
    if isinstance(payload.get("meta"), dict):
        return payload["meta"]
    return {
        "degraded": payload.get("degraded") or {"active": False, "reasons": [], "defaults_applied": []},
        "provenance": payload.get("provenance") or {},
        "confidence": payload.get("confidence"),
        "method": payload.get("method"),
    }


def _sample_endpoints() -> dict[str, Any]:
    client = TestClient(app)
    rows: list[dict[str, Any]] = []
    degraded_defaults = Counter()
    degraded_reasons = Counter()
    attestation_modes = Counter()
    snapshot_cache: dict[str, bool] = {}

    for spec in ENDPOINT_SPECS:
        started = time.perf_counter()
        request_kwargs: dict[str, Any] = {}
        if "json" in spec:
            request_kwargs["json"] = spec["json"]
        response = client.request(spec["method"].upper(), spec["path"], **request_kwargs)
        latency_ms = _round((time.perf_counter() - started) * 1000.0)

        payload: dict[str, Any] | None = None
        if "application/json" in (response.headers.get("content-type") or ""):
            try:
                payload = response.json()
            except Exception:
                payload = None

        meta = _extract_meta(payload) if isinstance(payload, dict) else {}
        degraded = meta.get("degraded") if isinstance(meta.get("degraded"), dict) else {}
        provenance = meta.get("provenance") if isinstance(meta.get("provenance"), dict) else {}
        snapshot_id = str(provenance.get("snapshot_id") or "") or None
        attestation = provenance.get("attestation") if isinstance(provenance.get("attestation"), dict) else {}
        attestation_mode = str(attestation.get("mode") or "missing")
        attestation_modes[attestation_mode] += 1

        provenance_verified = False
        if snapshot_id:
            if snapshot_id not in snapshot_cache:
                try:
                    snapshot_cache[snapshot_id] = bool(verify_snapshot(snapshot_id).get("valid"))
                except Exception:
                    snapshot_cache[snapshot_id] = False
            provenance_verified = snapshot_cache[snapshot_id]

        if degraded.get("active"):
            for item in degraded.get("defaults_applied") or []:
                degraded_defaults[str(item)] += 1
            for item in degraded.get("reasons") or []:
                degraded_reasons[str(item)] += 1

        rows.append(
            {
                "id": spec["id"],
                "method": spec["method"].upper(),
                "path": spec["path"],
                "status_code": response.status_code,
                "latency_ms": latency_ms,
                "within_latency_budget": latency_ms <= LATENCY_BUDGET_MS,
                "available": response.status_code == 200,
                "degraded_active": bool(degraded.get("active")),
                "defaults_applied": list(degraded.get("defaults_applied") or []),
                "degraded_reasons": list(degraded.get("reasons") or []),
                "snapshot_id": snapshot_id,
                "provenance_verified": provenance_verified,
                "attestation_mode": attestation_mode,
            }
        )

    return {
        "rows": rows,
        "degraded_defaults": dict(degraded_defaults),
        "degraded_reasons": dict(degraded_reasons),
        "attestation_modes": dict(attestation_modes),
    }


def _build_payload() -> dict[str, Any]:
    sampled = _sample_endpoints()
    rows = sampled["rows"]
    latencies = [float(row["latency_ms"]) for row in rows]
    available = [row for row in rows if row["available"]]
    degraded = [row for row in rows if row["degraded_active"]]
    provenance_rows = [row for row in rows if row["snapshot_id"]]
    verified_rows = [row for row in provenance_rows if row["provenance_verified"]]
    latest_snapshot = get_latest_snapshot(create_if_missing=True)
    if latest_snapshot is None:
        raise ArtifactError("Unable to resolve a current provenance snapshot.")
    latest_snapshot_audit = verify_snapshot(latest_snapshot.snapshot_id)
    transparency_audit = verify_log_integrity()
    authority_dashboard = _read_json(AUTHORITY_DASHBOARD)

    availability_pct = _percent(len(available), len(rows))
    request_health = {
        "sampled_endpoints": len(rows),
        "available_endpoints": len(available),
        "availability_pct": availability_pct,
        "meets_availability_budget": availability_pct >= AVAILABILITY_BUDGET_PCT,
        "critical_endpoints": rows,
    }
    degraded_mode = {
        "sampled_responses": len(rows),
        "degraded_responses": len(degraded),
        "degraded_rate_pct": _percent(len(degraded), len(rows)),
        "defaults_applied": sampled["degraded_defaults"],
        "reasons": sampled["degraded_reasons"],
    }
    provenance_verification = {
        "latest_snapshot_id": latest_snapshot.snapshot_id,
        "latest_snapshot_valid": bool(latest_snapshot_audit.get("valid")),
        "sampled_responses_with_snapshot": len(provenance_rows),
        "verified_sampled_responses": len(verified_rows),
        "verification_rate_pct": _percent(len(verified_rows), len(provenance_rows)),
        "attestation_modes": sampled["attestation_modes"],
        "transparency_log_valid": bool(transparency_audit.get("valid")),
    }
    latency_error_budgets = {
        "latency_budget_ms": LATENCY_BUDGET_MS,
        "availability_budget_pct": AVAILABILITY_BUDGET_PCT,
        "median_latency_ms": _round(float(median(latencies))) if latencies else 0.0,
        "p95_latency_ms": _p95(latencies),
        "max_latency_ms": _round(max(latencies)) if latencies else 0.0,
        "within_latency_budget_count": sum(1 for row in rows if row["within_latency_budget"]),
        "error_budget_burn_pct": _round(max(0.0, 100.0 - availability_pct)),
    }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "release_track": "public-beta-v3",
        "request_health": request_health,
        "degraded_mode": degraded_mode,
        "provenance_verification": provenance_verification,
        "latency_error_budgets": latency_error_budgets,
        "context": {
            "authority_conformance_pass_rate": authority_dashboard.get("pipeline_health", {}).get("conformance_pass_rate"),
            "authority_catalog_coverage_pct": authority_dashboard.get("pipeline_health", {}).get("rule_catalog_coverage_pct"),
        },
    }


def _build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Dashboard Metrics",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Release Track: `{payload['release_track']}`",
        "",
        "## Request Health",
        "",
        f"- Sampled endpoints: {payload['request_health']['sampled_endpoints']}",
        f"- Availability: {payload['request_health']['availability_pct']}%",
        f"- Meets availability budget: {payload['request_health']['meets_availability_budget']}",
        "",
        "## Degraded Mode",
        "",
        f"- Degraded response rate: {payload['degraded_mode']['degraded_rate_pct']}%",
        "",
        "## Provenance Verification",
        "",
        f"- Latest snapshot: `{payload['provenance_verification']['latest_snapshot_id']}`",
        f"- Latest snapshot valid: {payload['provenance_verification']['latest_snapshot_valid']}",
        f"- Verification rate: {payload['provenance_verification']['verification_rate_pct']}%",
        f"- Transparency log valid: {payload['provenance_verification']['transparency_log_valid']}",
        "",
        "## Latency Budgets",
        "",
        f"- Median latency: {payload['latency_error_budgets']['median_latency_ms']} ms",
        f"- P95 latency: {payload['latency_error_budgets']['p95_latency_ms']} ms",
        f"- Max latency: {payload['latency_error_budgets']['max_latency_ms']} ms",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    try:
        payload = _build_payload()
    except ArtifactError as exc:
        print(f"[FAIL] {exc}")
        return 1

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    OUT_MD.write_text(_build_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
