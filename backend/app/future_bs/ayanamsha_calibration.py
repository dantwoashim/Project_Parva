"""Ayanamsha calibration scaffolding."""

from __future__ import annotations

from typing import Any

from .ayanamsha import AYANAMSHA_CANDIDATES


def ayanamsha_calibration_summary() -> dict[str, Any]:
    return {
        "active": "lahiri",
        "candidates": [candidate.payload() for candidate in AYANAMSHA_CANDIDATES.values()],
        "calibration_mode": "candidate_registry_not_empirical_calibration",
        "status": "lahiri_active_other_candidates_registered_for_sensitivity",
        "note": (
            "Non-Lahiri candidates are registered but not yet used as independent "
            "production ephemeris calculations until per-call sidereal mode support "
            "and verified calibration are added."
        ),
    }
