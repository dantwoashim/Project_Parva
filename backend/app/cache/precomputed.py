"""Helpers for reading precomputed panchanga/festival artifacts."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, Optional

from app.reliability.metrics import get_metrics_registry

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PRECOMPUTE_DIR = PROJECT_ROOT / "output" / "precomputed"
METRICS = get_metrics_registry()


def _read_json(path: Path) -> Optional[dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_precomputed_panchanga(target_date: date) -> Optional[dict[str, Any]]:
    year_file = PRECOMPUTE_DIR / f"panchanga_{target_date.year}.json"
    payload = _read_json(year_file)
    if not payload:
        METRICS.record_cache_lookup("panchanga", False)
        return None
    row = payload.get("dates", {}).get(target_date.isoformat())
    METRICS.record_cache_lookup("panchanga", row is not None)
    return row


def load_precomputed_festival_year(year: int) -> Optional[dict[str, Any]]:
    path = PRECOMPUTE_DIR / f"festivals_{year}.json"
    payload = _read_json(path)
    METRICS.record_cache_lookup("festival_year", payload is not None)
    return payload


def load_precomputed_festivals_between(start_date: date, end_date: date) -> Optional[list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []

    for year in range(start_date.year, end_date.year + 1):
        payload = load_precomputed_festival_year(year)
        if not payload or not isinstance(payload.get("festivals"), list):
            return None

        for row in payload["festivals"]:
            try:
                festival_start = date.fromisoformat(str(row["start"]))
                festival_end = date.fromisoformat(str(row["end"]))
            except Exception:
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

    return rows


def get_cache_stats() -> dict[str, Any]:
    PRECOMPUTE_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(PRECOMPUTE_DIR.glob("*.json"))
    total_bytes = sum(f.stat().st_size for f in files)
    return {
        "directory": str(PRECOMPUTE_DIR),
        "file_count": len(files),
        "total_bytes": total_bytes,
        "files": [
            {
                "name": f.name,
                "size": f.stat().st_size,
                "modified": f.stat().st_mtime,
            }
            for f in files
        ],
    }
