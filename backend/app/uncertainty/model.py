"""Uncertainty object builders for API responses."""

from __future__ import annotations

from typing import Any, Dict

from .calibration import load_calibration_model


def _level_params(level: str, calibration: Dict[str, Any]) -> Dict[str, float]:
    levels = calibration.get("levels", {})
    return levels.get(level, levels.get("uncertain", {"probability": 0.75, "interval_hours": 48.0}))


def build_uncertainty(
    level: str,
    *,
    methodology: str,
    calibration: Dict[str, Any] | None = None,
    interval_hours: float | None = None,
    notes: str | None = None,
    boundary_proximity_minutes: float | None = None,
) -> Dict[str, Any]:
    model = calibration or load_calibration_model()
    params = _level_params(level, model)
    interval = float(interval_hours if interval_hours is not None else params.get("interval_hours", 48.0))
    out: Dict[str, Any] = {
        "level": level,
        "probability": round(float(params.get("probability", 0.75)), 4),
        "interval_hours": interval,
        "calibration_data_size": int(model.get("data_points", 0)),
        "methodology": methodology,
    }
    if notes:
        out["notes"] = notes
    if boundary_proximity_minutes is not None:
        out["boundary_proximity_minutes"] = round(float(boundary_proximity_minutes), 2)
    return out


def build_bs_uncertainty(bs_confidence: str, estimated_error_days: str | None = None) -> Dict[str, Any]:
    if bs_confidence == "official":
        return build_uncertainty("exact", methodology="official_lookup_table")
    if bs_confidence == "estimated":
        return build_uncertainty(
            "estimated",
            methodology="bs_estimation_model",
            interval_hours=24.0,
            notes=f"estimated_error_days={estimated_error_days or '0-1'}",
        )
    return build_uncertainty("uncertain", methodology="unknown_bs_mode")


def estimate_boundary_proximity_minutes(progress: float | None) -> float | None:
    if progress is None:
        return None
    # Avg tithi duration ≈ 23.6h. Distance to nearest boundary in minutes.
    nearest = min(abs(float(progress)), abs(1.0 - float(progress)))
    return nearest * 23.6 * 60.0


def build_tithi_uncertainty(
    *,
    method: str,
    confidence: str,
    progress: float | None = None,
) -> Dict[str, Any]:
    boundary_minutes = estimate_boundary_proximity_minutes(progress)

    if method == "ephemeris_udaya" and confidence == "exact":
        level = "exact"
        interval = 0.5
        notes = "sunrise-based ephemeris calculation"
    elif method == "instantaneous":
        level = "confident"
        interval = 6.0
        notes = "fallback instantaneous calculation"
    else:
        level = "uncertain"
        interval = 24.0
        notes = "unclassified tithi method"

    # Boundary-sensitive case: widen interval and lower level.
    if boundary_minutes is not None and boundary_minutes <= 30:
        level = "uncertain"
        interval = max(interval, 12.0)
        notes = "tithi boundary close to sunrise"

    return build_uncertainty(
        level,
        methodology=method,
        interval_hours=interval,
        notes=notes,
        boundary_proximity_minutes=boundary_minutes,
    )


def build_panchanga_uncertainty() -> Dict[str, Any]:
    return build_uncertainty(
        "exact",
        methodology="ephemeris_panchanga",
        interval_hours=0.5,
        notes="astronomical panchanga computation",
    )
