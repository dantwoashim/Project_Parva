"""Helpers for reading precomputed panchanga/festival artifacts."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PRECOMPUTE_DIR = PROJECT_ROOT / "output" / "precomputed"


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
        return None
    return payload.get("dates", {}).get(target_date.isoformat())


def load_precomputed_festival_year(year: int) -> Optional[dict[str, Any]]:
    path = PRECOMPUTE_DIR / f"festivals_{year}.json"
    return _read_json(path)


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
