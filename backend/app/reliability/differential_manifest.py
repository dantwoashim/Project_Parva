"""Differential validation manifest helpers."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DIFF_DATA_PATH = PROJECT_ROOT / "data" / "differential" / "disagreements.json"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return {}


def _sha256_path(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def get_differential_manifest() -> dict[str, Any]:
    payload = _read_json(DIFF_DATA_PATH)
    result = payload.get("result", {}) if isinstance(payload.get("result"), dict) else {}
    taxonomy = result.get("taxonomy", {}) if isinstance(result.get("taxonomy"), dict) else {}
    gate = payload.get("gate", {}) if isinstance(payload.get("gate"), dict) else {}

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "report_generated_at": payload.get("generated_at"),
        "current_report": payload.get("current"),
        "baseline_report": payload.get("baseline"),
        "total_compared": result.get("total_compared", 0),
        "drift_percent": result.get("drift_percent", 0.0),
        "taxonomy": taxonomy,
        "gate": {
            "max_drift": gate.get("max_drift", 2.0),
            "strict": gate.get("strict", False),
            "passed": gate.get("passed", False),
            "major_count": gate.get("major_count", 0),
        },
        "report_hash": _sha256_path(DIFF_DATA_PATH),
        "sample_details": (result.get("details") or [])[:5],
        "known_limits": [
            "Differential analysis is only as broad as the current benchmark report pair.",
            "Agreement here does not replace authority-backed evaluation for festival conflict classes.",
            "This surface is strongest for regression drift detection, not for declaring universal truth.",
        ],
    }


__all__ = ["get_differential_manifest"]
