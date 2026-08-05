"""Immutable model-run registry for future BS predictions."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.research.future_bs.paths import project_root

from .corpus import CORPUS_VERSION
from .models import CALIBRATION_VERSION, METHOD_VERSION

PROJECT_ROOT = project_root()
RUNS_DIR = PROJECT_ROOT / "data" / "future_bs" / "model_runs"
DEFAULT_RUN_ID = "parva_authority_aware_solar_civil_v7_cutoff_2083"


def _stable_hash(payload: dict[str, Any]) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(data).hexdigest()


def build_run_metadata(
    *,
    run_id: str = DEFAULT_RUN_ID,
    start_bs: int = 2084,
    end_bs: int = 2200,
    created_at: str = "2026-08-05T00:00:00Z",
) -> dict[str, Any]:
    try:
        from .solar_ingress_engine import active_ephemeris_label

        ephemeris_version = (
            "jpl_de440_lahiri_sidereal"
            if active_ephemeris_label() == "jpl_de440"
            else "swiss_moshier_lahiri_sidereal"
        )
    except (ImportError, RuntimeError, TypeError, ValueError):
        ephemeris_version = "unknown"
    payload = {
        "run_id": run_id,
        "model_version": METHOD_VERSION,
        "calibration_version": CALIBRATION_VERSION,
        "corpus_version": CORPUS_VERSION,
        "ephemeris_version": ephemeris_version,
        "ayanamsha_version": "lahiri_with_registered_sensitivity_candidates_v1",
        "civil_rule_version": "source_stratified_month_start_reconciliation_v1",
        "rule_version": "authority_aware_solar_civil_v7",
        "training_cutoff_bs_year": 2083,
        "training_source_policy": "source_stratified",
        "leakage_safe": True,
        "prediction_range": f"{start_bs}-{end_bs} BS",
        "created_at": created_at,
        "publication_status": "computed_prediction_not_official",
    }
    payload["hash"] = _stable_hash(payload)
    return payload


def write_run_metadata(metadata: dict[str, Any]) -> Path:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    path = RUNS_DIR / f"{metadata['run_id']}.json"
    path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def list_model_runs() -> list[dict[str, Any]]:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    runs: list[dict[str, Any]] = []
    for path in sorted(RUNS_DIR.glob("*.json")):
        runs.append(json.loads(path.read_text(encoding="utf-8")))
    if not runs:
        runs.append(build_run_metadata(created_at=datetime.now(timezone.utc).isoformat()))
    return runs


def get_model_run(run_id: str) -> dict[str, Any]:
    path = RUNS_DIR / f"{run_id}.json"
    if not path.exists():
        if run_id == DEFAULT_RUN_ID:
            return build_run_metadata()
        raise ValueError(f"Unknown model run: {run_id}")
    return json.loads(path.read_text(encoding="utf-8"))
