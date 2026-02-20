"""Shared parsing + metadata helpers for personal-stack API endpoints."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

from fastapi import HTTPException

from app.policy import get_policy_metadata
from app.provenance import get_provenance_payload

DEFAULT_LAT = 27.7172
DEFAULT_LON = 85.3240
DEFAULT_TZ = "Asia/Kathmandu"


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


def normalize_coordinates(lat_raw: Optional[str], lon_raw: Optional[str]) -> Tuple[float, float, List[str]]:
    warnings: list[str] = []

    def _parse(raw: Optional[str], *, fallback: float, lo: float, hi: float, name: str) -> float:
        if raw is None or raw.strip() == "":
            warnings.append(f"Missing {name}; using default {fallback}.")
            return fallback
        try:
            value = float(raw)
        except ValueError:
            warnings.append(f"Invalid {name} '{raw}'; using default {fallback}.")
            return fallback
        if not (lo <= value <= hi):
            warnings.append(f"Out-of-range {name} '{raw}'; using default {fallback}.")
            return fallback
        return value

    lat = _parse(lat_raw, fallback=DEFAULT_LAT, lo=-90.0, hi=90.0, name="lat")
    lon = _parse(lon_raw, fallback=DEFAULT_LON, lo=-180.0, hi=180.0, name="lon")
    return lat, lon, warnings


def base_meta_payload(
    *,
    trace_id: str,
    confidence: str,
    method: str,
    method_profile: Optional[str] = None,
    quality_band: str = "validated",
    assumption_set_id: str = "np-mainstream-v1",
    advisory_scope: str = "informational",
) -> Dict[str, Any]:
    return {
        "engine_version": "v3",
        "calculation_trace_id": trace_id,
        "confidence": confidence,
        "method": method,
        "method_profile": method_profile or method,
        "quality_band": quality_band,
        "assumption_set_id": assumption_set_id,
        "advisory_scope": advisory_scope,
        "provenance": get_provenance_payload(verify_url="/v3/api/provenance/root", create_if_missing=True),
        "policy": get_policy_metadata(),
    }
