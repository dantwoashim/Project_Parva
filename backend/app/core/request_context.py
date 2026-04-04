"""Shared parsing + metadata helpers for personal-stack API endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from math import isfinite
from typing import Any, Dict, List, Optional, Tuple, TypeAlias
from zoneinfo import ZoneInfo

from fastapi import HTTPException

from app.policy import get_policy_metadata
from app.provenance import get_provenance_payload

DEFAULT_LAT = 27.7172
DEFAULT_LON = 85.3240
DEFAULT_TZ = "Asia/Kathmandu"
CoordinateInput: TypeAlias = str | int | float | None


@dataclass(frozen=True)
class DegradedState:
    active: bool
    reasons: tuple[str, ...]
    defaults_applied: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "active": self.active,
            "reasons": list(self.reasons),
            "defaults_applied": list(self.defaults_applied),
        }


def parse_date(date_str: str) -> date:
    try:
        return date.fromisoformat(date_str)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD") from exc


def parse_datetime(datetime_str: str, *, tz_name: str) -> datetime:
    normalized = datetime_str.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid datetime format. Use ISO8601, e.g. 2026-02-15T06:30:00+05:45",
        ) from exc

    if dt.tzinfo is None:
        try:
            dt = dt.replace(tzinfo=ZoneInfo(tz_name))
        except Exception:
            dt = dt.replace(tzinfo=ZoneInfo(DEFAULT_TZ))
    return dt


def normalize_timezone(tz_name: Optional[str]) -> Tuple[str, List[str]]:
    warnings: list[str] = []
    tz_candidate = (tz_name or DEFAULT_TZ).strip() or DEFAULT_TZ
    try:
        ZoneInfo(tz_candidate)
        return tz_candidate, warnings
    except Exception:
        warnings.append(f"Invalid timezone '{tz_candidate}', using {DEFAULT_TZ}.")
        return DEFAULT_TZ, warnings


def _parse_coordinate(
    raw: CoordinateInput,
    *,
    fallback: float,
    lo: float,
    hi: float,
    name: str,
    warnings: list[str],
) -> float:
    if raw is None:
        warnings.append(f"Missing {name}; using default {fallback}.")
        return fallback

    if isinstance(raw, str):
        candidate = raw.strip()
        if candidate == "":
            warnings.append(f"Missing {name}; using default {fallback}.")
            return fallback
    else:
        candidate = str(raw)

    try:
        value = float(candidate)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {name}. Use a finite decimal between {lo} and {hi}.",
        ) from exc

    if not isfinite(value):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {name}. Use a finite decimal between {lo} and {hi}.",
        )

    if not (lo <= value <= hi):
        raise HTTPException(
            status_code=400,
            detail=f"Out-of-range {name}. Use a value between {lo} and {hi}.",
        )

    # Canonicalize through float parsing so GET query strings and POST numbers normalize identically.
    return float(f"{value:.12g}")


def normalize_coordinates(
    lat_raw: CoordinateInput, lon_raw: CoordinateInput
) -> Tuple[float, float, List[str]]:
    warnings: list[str] = []

    lat = _parse_coordinate(
        lat_raw, fallback=DEFAULT_LAT, lo=-90.0, hi=90.0, name="lat", warnings=warnings
    )
    lon = _parse_coordinate(
        lon_raw, fallback=DEFAULT_LON, lo=-180.0, hi=180.0, name="lon", warnings=warnings
    )
    return lat, lon, warnings


def _is_blank(value: CoordinateInput | Optional[str]) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    return False


def build_input_degraded_state(
    *,
    lat_raw: CoordinateInput,
    lon_raw: CoordinateInput,
    tz_raw: Optional[str],
    tz_warnings: List[str],
) -> DegradedState:
    defaults_applied: list[str] = []
    reasons: list[str] = []

    if _is_blank(lat_raw):
        defaults_applied.append("latitude")
    if _is_blank(lon_raw):
        defaults_applied.append("longitude")
    if "latitude" in defaults_applied or "longitude" in defaults_applied:
        reasons.append("location_defaulted")

    if _is_blank(tz_raw):
        defaults_applied.append("timezone")
        reasons.append("timezone_defaulted")
    elif tz_warnings:
        defaults_applied.append("timezone")
        reasons.append("timezone_invalid")

    return DegradedState(
        active=bool(defaults_applied),
        reasons=tuple(dict.fromkeys(reasons)),
        defaults_applied=tuple(dict.fromkeys(defaults_applied)),
    )


def derive_support_tier(
    *,
    confidence: str,
    quality_band: str,
    degraded: Optional[DegradedState] = None,
) -> str:
    normalized_confidence = (confidence or "unknown").strip().lower()
    normalized_band = (quality_band or "").strip().lower()
    degraded_state = degraded or DegradedState(active=False, reasons=tuple(), defaults_applied=tuple())

    if normalized_confidence == "official":
        return "authoritative"
    if normalized_confidence == "estimated":
        return "estimated"
    if degraded_state.active:
        return "heuristic"
    if normalized_band in {"beta", "research", "inventory", "provisional"}:
        return "heuristic"
    return "computed"


def _fallback_used(method: str) -> bool:
    normalized = str(method or "").strip().lower()
    return "fallback" in normalized or "legacy" in normalized


def _calibration_status(*, confidence: str, method: str) -> str:
    normalized_confidence = (confidence or "").strip().lower()
    normalized_method = (method or "").strip().lower()
    if normalized_confidence == "official" or normalized_method == "override":
        return "not_applicable"
    return "unavailable"


def base_meta_payload(
    *,
    trace_id: str,
    confidence: str,
    method: str,
    method_profile: Optional[str] = None,
    quality_band: str = "validated",
    assumption_set_id: str = "np-mainstream-v1",
    advisory_scope: str = "informational",
    degraded: Optional[DegradedState] = None,
    engine_path: Optional[str] = None,
    fallback_used: Optional[bool] = None,
    calibration_status: Optional[str] = None,
) -> Dict[str, Any]:
    degraded_state = degraded or DegradedState(active=False, reasons=tuple(), defaults_applied=tuple())
    return {
        "engine_version": "v3",
        "calculation_trace_id": trace_id,
        "confidence": confidence,
        "support_tier": derive_support_tier(
            confidence=confidence,
            quality_band=quality_band,
            degraded=degraded_state,
        ),
        "method": method,
        "method_profile": method_profile or method,
        "engine_path": engine_path or method,
        "fallback_used": _fallback_used(method) if fallback_used is None else fallback_used,
        "calibration_status": (
            _calibration_status(confidence=confidence, method=method)
            if calibration_status is None
            else calibration_status
        ),
        "quality_band": quality_band,
        "assumption_set_id": assumption_set_id,
        "advisory_scope": advisory_scope,
        "degraded": degraded_state.to_dict(),
        "provenance": get_provenance_payload(
            verify_url="/v3/api/provenance/root", create_if_missing=True
        ),
        "policy": get_policy_metadata(),
    }


__all__ = [
    "CoordinateInput",
    "DEFAULT_LAT",
    "DEFAULT_LON",
    "DEFAULT_TZ",
    "DegradedState",
    "base_meta_payload",
    "build_input_degraded_state",
    "derive_support_tier",
    "normalize_coordinates",
    "normalize_timezone",
    "parse_date",
    "parse_datetime",
]
