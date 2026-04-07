"""Helpers for reading precomputed panchanga/festival artifacts."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Optional

from app.infrastructure.precomputed_store import (
    FilePrecomputedArtifactStore,
)
from app.reliability.metrics import get_metrics_registry

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PRECOMPUTE_DIR = PROJECT_ROOT / "output" / "precomputed"
METRICS = get_metrics_registry()


def get_precomputed_store() -> FilePrecomputedArtifactStore:
    return FilePrecomputedArtifactStore(PRECOMPUTE_DIR, METRICS)


def clear_precomputed_cache() -> None:
    get_precomputed_store().clear()


def load_precomputed_panchanga(target_date: date) -> Optional[dict[str, Any]]:
    return get_precomputed_store().load_panchanga(target_date)


def load_precomputed_festival_year(year: int) -> Optional[dict[str, Any]]:
    return get_precomputed_store().load_festival_year(year)


def load_precomputed_festivals_between_report(
    start_date: date,
    end_date: date,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    loaded_years: list[int] = []
    missing_years: list[int] = []

    for year in range(start_date.year, end_date.year + 1):
        payload = load_precomputed_festival_year(year)
        if not payload or not isinstance(payload.get("festivals"), list):
            missing_years.append(year)
            continue

        loaded_years.append(year)
        for row in payload["festivals"]:
            try:
                festival_start = date.fromisoformat(str(row["start"]))
                festival_end = date.fromisoformat(str(row["end"]))
            except (KeyError, TypeError, ValueError):
                continue

            if festival_end < start_date or festival_start > end_date:
                continue

            rows.append(
                {
                    "festival_id": row["festival_id"],
                    "start_date": festival_start,
                    "end_date": festival_end,
                    "year": year,
                    "method": row.get("method", "precomputed"),
                    "lunar_month": row.get("lunar_month"),
                    "is_adhik_year": bool(row.get("is_adhik_year", False)),
                }
            )

    return {
        "rows": rows,
        "loaded_years": loaded_years,
        "missing_years": missing_years,
        "partial_hit": bool(loaded_years) and bool(missing_years),
        "full_hit": bool(loaded_years) and not missing_years,
    }


def load_precomputed_festivals_between(
    start_date: date,
    end_date: date,
) -> Optional[list[dict[str, Any]]]:
    report = load_precomputed_festivals_between_report(start_date, end_date)
    if report["missing_years"]:
        return None
    return report["rows"]


def prewarm_hot_set(today: Optional[date] = None) -> dict[str, Any]:
    return get_precomputed_store().prewarm_hot_set(today)


def measure_hotset_latency(today: Optional[date] = None) -> dict[str, Any]:
    return get_precomputed_store().measure_hotset_latency(today)


def get_cache_stats() -> dict[str, Any]:
    return get_precomputed_store().get_stats()
