"""Temporal Compass API for cockpit-style home route."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.domain.temporal_context import CalendarContext, LocationContext
from app.explainability import create_reason_trace
from app.services.compass_service import build_temporal_compass
from app.services.trust_surface_service import (
    build_portable_proof_capsule,
    build_temporal_risk_payload,
)

from ._personal_utils import (
    CoordinateInput,
    base_meta_payload,
    normalize_coordinates,
    normalize_timezone,
    parse_date,
)

router = APIRouter(prefix="/api/temporal", tags=["temporal"])


class TemporalCompassRequest(BaseModel):
    date: str = Field(..., description="Gregorian date in YYYY-MM-DD format")
    lat: CoordinateInput = Field(None, description="Latitude")
    lon: CoordinateInput = Field(None, description="Longitude")
    tz: Optional[str] = Field("Asia/Kathmandu", description="IANA timezone")
    quality_band: str = Field("computed", description="computed|provisional|inventory|all")
    risk_mode: str = Field("standard", description="standard|strict")


def _build_temporal_compass_response(
    *,
    date_str: str,
    lat: CoordinateInput,
    lon: CoordinateInput,
    tz: Optional[str],
    quality_band: str,
    risk_mode: str,
):
    target_date = parse_date(date_str)
    latitude, longitude, coord_warnings = normalize_coordinates(lat, lon)
    timezone_name, tz_warnings = normalize_timezone(tz)

    payload = build_temporal_compass(
        target_date=target_date,
        latitude=latitude,
        longitude=longitude,
        timezone_name=timezone_name,
        quality_band=quality_band,
    )

    trace = create_reason_trace(
        trace_type="temporal_compass",
        subject={"date": target_date.isoformat()},
        inputs={
            "date": target_date.isoformat(),
            "lat": latitude,
            "lon": longitude,
            "tz": timezone_name,
        },
        outputs={
            "tithi": payload["primary_readout"].get("tithi_name"),
            "festival_count": payload.get("today", {}).get("count", 0),
            "best_window": payload.get("horizon", {}).get("current_muhurta", {}).get("name"),
        },
        steps=[
            {"step": "panchanga", "detail": "Computed daily panchanga markers for location."},
            {"step": "muhurta", "detail": "Derived best window and avoid windows for the day."},
            {"step": "festivals", "detail": "Resolved festivals active on the selected date."},
        ],
    )

    meta = base_meta_payload(
        trace_id=trace["trace_id"],
        confidence="computed",
        method="ephemeris_udaya",
        method_profile="temporal_compass_v1",
        quality_band="validated",
        assumption_set_id="np-mainstream-v2",
        advisory_scope="informational",
    )
    risk = build_temporal_risk_payload(
        progress=(payload.get("primary_readout") or {}).get("phase_progress"),
        support_tier=str(meta["support_tier"]),
        fallback_used=bool(meta["fallback_used"]),
        method=str(meta["engine_path"]),
        risk_mode=risk_mode,
    )

    return {
        **payload,
        "warnings": coord_warnings + tz_warnings,
        "location_context": LocationContext(
            latitude=latitude,
            longitude=longitude,
            timezone_name=timezone_name,
            source="temporal_compass_request",
        ).as_dict(),
        **meta,
        **risk,
    }


def _build_temporal_compass_proof_capsule(
    *,
    payload: dict,
    request: dict,
) -> dict:
    return build_portable_proof_capsule(
        surface="temporal_compass",
        payload=payload,
        request=request,
        calendar_context=CalendarContext(
            target_date=parse_date(str(request["date"])),
            surface="temporal_compass",
            risk_mode=str(request.get("risk_mode") or "standard"),
            support_tier=str(payload.get("support_tier") or ""),
            snapshot_id=((payload.get("provenance") or {}).get("snapshot_id")),
        ),
        location_context=LocationContext(
            latitude=request.get("lat"),
            longitude=request.get("lon"),
            timezone_name=request.get("tz"),
            source="temporal_compass_request",
        ),
        source_lineage={
            "quality_band_filter": payload.get("quality_band_filter"),
            "warnings": payload.get("warnings"),
            "ephemeris": payload.get("engine"),
        },
    )


@router.get("/compass")
async def temporal_compass(
    date_str: str = Query(..., alias="date", description="Gregorian date in YYYY-MM-DD format"),
    lat: Optional[str] = Query(None, description="Latitude"),
    lon: Optional[str] = Query(None, description="Longitude"),
    tz: Optional[str] = Query("Asia/Kathmandu", description="IANA timezone"),
    quality_band: str = Query("computed", description="computed|provisional|inventory|all"),
    risk_mode: str = Query("standard", description="standard|strict"),
):
    return _build_temporal_compass_response(
        date_str=date_str,
        lat=lat,
        lon=lon,
        tz=tz,
        quality_band=quality_band,
        risk_mode=risk_mode,
    )


@router.post("/compass")
async def temporal_compass_post(payload: TemporalCompassRequest):
    return _build_temporal_compass_response(
        date_str=payload.date,
        lat=payload.lat,
        lon=payload.lon,
        tz=payload.tz,
        quality_band=payload.quality_band,
        risk_mode=payload.risk_mode,
    )


@router.get("/compass/proof-capsule")
async def temporal_compass_proof_capsule(
    date_str: str = Query(..., alias="date", description="Gregorian date in YYYY-MM-DD format"),
    lat: Optional[str] = Query(None, description="Latitude"),
    lon: Optional[str] = Query(None, description="Longitude"),
    tz: Optional[str] = Query("Asia/Kathmandu", description="IANA timezone"),
    quality_band: str = Query("computed", description="computed|provisional|inventory|all"),
    risk_mode: str = Query("strict", description="standard|strict"),
):
    payload = _build_temporal_compass_response(
        date_str=date_str,
        lat=lat,
        lon=lon,
        tz=tz,
        quality_band=quality_band,
        risk_mode=risk_mode,
    )
    return _build_temporal_compass_proof_capsule(
        payload=payload,
        request={
            "date": date_str,
            "lat": lat,
            "lon": lon,
            "tz": tz,
            "quality_band": quality_band,
            "risk_mode": risk_mode,
        },
    )


@router.post("/compass/proof-capsule")
async def temporal_compass_proof_capsule_post(payload: TemporalCompassRequest):
    response_payload = _build_temporal_compass_response(
        date_str=payload.date,
        lat=payload.lat,
        lon=payload.lon,
        tz=payload.tz,
        quality_band=payload.quality_band,
        risk_mode=payload.risk_mode,
    )
    return _build_temporal_compass_proof_capsule(
        payload=response_payload,
        request={
            "date": payload.date,
            "lat": payload.lat,
            "lon": payload.lon,
            "tz": payload.tz,
            "quality_band": payload.quality_band,
            "risk_mode": payload.risk_mode,
        },
    )
