"""SLO evaluation utilities for Year-3 reliability tracking."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class SLOTarget:
    name: str
    target: float
    comparator: str  # <= or >=
    source: str


SLO_TARGETS = [
    SLOTarget("p95_latency_ms", 500.0, "<=", "reports/loadtest_m29.json"),
    SLOTarget("cache_hit_ratio_panchanga", 0.90, ">=", "reports/loadtest_m29.json"),
    SLOTarget("differential_drift_percent", 2.0, "<=", "reports/differential_report.json"),
]


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _extract_metric(metric: str, payload: dict[str, Any] | None) -> float | None:
    if payload is None:
        return None
    if metric == "p95_latency_ms":
        return float(payload.get("latency_ms", {}).get("p95", 0.0))
    if metric == "cache_hit_ratio_panchanga":
        return float(payload.get("cache_hit_ratio", 0.0))
    if metric == "differential_drift_percent":
        return float(payload.get("result", {}).get("drift_percent", 0.0))
    return None


def _passes(comparator: str, actual: float | None, target: float) -> bool | None:
    if actual is None:
        return None
    if comparator == "<=":
        return actual <= target
    if comparator == ">=":
        return actual >= target
    return None


def evaluate_slos() -> dict[str, Any]:
    rows = []
    overall = True
    for target in SLO_TARGETS:
        path = PROJECT_ROOT / target.source
        payload = _read_json(path)
        actual = _extract_metric(target.name, payload)
        passed = _passes(target.comparator, actual, target.target)
        if passed is False:
            overall = False
        rows.append(
            {
                "name": target.name,
                "target": target.target,
                "comparator": target.comparator,
                "actual": actual,
                "passed": passed,
                "source": target.source,
                "available": payload is not None,
            }
        )

    return {
        "overall_passed": overall and all(r["passed"] is not None for r in rows),
        "rows": rows,
    }
