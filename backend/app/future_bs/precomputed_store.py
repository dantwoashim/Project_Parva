"""Precomputed prediction store for fast API responses."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from .models import METHOD_VERSION
from .run_registry import DEFAULT_RUN_ID

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PREDICTIONS_DIR = PROJECT_ROOT / "data" / "future_bs" / "predictions"
DEFAULT_PREDICTION_FILE = PREDICTIONS_DIR / f"{METHOD_VERSION}_2084_2200.json"


def live_compute_enabled() -> bool:
    return os.getenv("PARVA_FUTURE_BS_LIVE_COMPUTE", "0").strip().lower() in {"1", "true", "yes"}


@lru_cache(maxsize=1)
def load_precomputed_predictions() -> dict[str, Any]:
    if not DEFAULT_PREDICTION_FILE.exists():
        return {
            "available": False,
            "run_id": DEFAULT_RUN_ID,
            "years": {},
        }
    payload = json.loads(DEFAULT_PREDICTION_FILE.read_text(encoding="utf-8"))
    years = {int(year): value for year, value in payload.get("years", {}).items()}
    payload["years"] = years
    payload["available"] = True
    return payload


def get_precomputed_year(bs_year: int) -> dict[str, Any] | None:
    payload = load_precomputed_predictions()
    year_payload = payload.get("years", {}).get(bs_year)
    if not year_payload:
        return None
    result = dict(year_payload)
    result["served_from"] = "precomputed_prediction_store"
    result.setdefault("run_id", payload.get("run_id", DEFAULT_RUN_ID))
    result.setdefault("publication_status", "not_official_publication")
    return result


def precomputed_store_status() -> dict[str, Any]:
    payload = load_precomputed_predictions()
    years = sorted(payload.get("years", {}))
    return {
        "available": payload.get("available", False),
        "path": str(DEFAULT_PREDICTION_FILE.relative_to(PROJECT_ROOT)),
        "run_id": payload.get("run_id", DEFAULT_RUN_ID),
        "method_version": payload.get("method_version", METHOD_VERSION),
        "year_count": len(years),
        "range": f"{years[0]}-{years[-1]} BS" if years else None,
        "live_compute_enabled": live_compute_enabled(),
    }
