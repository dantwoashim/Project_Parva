"""Load uncertainty calibration model from reports artifact."""

from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CALIBRATION_FILE = PROJECT_ROOT / "reports" / "uncertainty_calibration.json"


def default_calibration() -> Dict[str, Any]:
    return {
        "generated_at": None,
        "data_points": 0,
        "calibration_mode": "unavailable",
        "levels": {
            "exact": {"probability": 0.6, "interval_hours": 1.0},
            "confident": {"probability": 0.52, "interval_hours": 8.0},
            "estimated": {"probability": 0.44, "interval_hours": 24.0},
            "uncertain": {"probability": 0.32, "interval_hours": 48.0},
            "degraded": {"probability": 0.25, "interval_hours": 72.0},
        },
    }


def load_calibration_model(path: Path | None = None) -> Dict[str, Any]:
    source = path or DEFAULT_CALIBRATION_FILE
    if source.exists():
        try:
            payload = json.loads(source.read_text(encoding="utf-8"))
            if isinstance(payload, dict) and "levels" in payload:
                payload.setdefault(
                    "calibration_mode",
                    "empirical" if int(payload.get("data_points", 0) or 0) > 0 else "unavailable",
                )
                return payload
        except (OSError, JSONDecodeError, TypeError, ValueError):
            return default_calibration()
    return default_calibration()
