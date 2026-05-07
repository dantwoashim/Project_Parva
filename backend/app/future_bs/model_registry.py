"""Future BS model registry."""

from __future__ import annotations

from typing import Any

from .ayanamsha_calibration import ayanamsha_calibration_summary
from .ephemeris import JPLDe440Adapter, MoshierAdapter, SwissEphemerisAdapter
from .models import CALIBRATION_VERSION, METHOD_VERSION


def model_registry_payload() -> dict[str, Any]:
    adapters = [JPLDe440Adapter(), SwissEphemerisAdapter(), MoshierAdapter()]
    jpl_available = adapters[0].available
    return {
        "method_version": METHOD_VERSION,
        "calibration_version": CALIBRATION_VERSION,
        "primary_model_family": "computational_solar_ingress",
        "ephemeris_adapters": [adapter.payload() for adapter in adapters],
        "ayanamsha": ayanamsha_calibration_summary(),
        "models": [
            {
                "name": "jpl_de440_lahiri_same_day",
                "status": "active" if jpl_available else "registered_unavailable_until_kernel_configured",
                "weight": 1.0 if jpl_available else 0.0,
            },
            {
                "name": "jpl_de440_lahiri_sunrise",
                "status": "active" if jpl_available else "registered_unavailable_until_kernel_configured",
                "weight": 1.0 if jpl_available else 0.0,
            },
            {
                "name": "swiss_lahiri_civil_rule_ensemble",
                "status": "active",
                "weight": 1.0,
            },
            {
                "name": "swiss_moshier_lahiri_civil_rule_ensemble",
                "status": "active_fallback",
                "weight": 1.0,
            },
            {
                "name": "legacy_cycle_predictor",
                "status": "weak_fallback_vote",
                "weight": 0.65,
            },
        ],
        "claim_boundary": (
            "DE440 is configured and available."
            if jpl_available
            else "DE440 models are registered but unavailable until a kernel is configured."
        ),
    }
