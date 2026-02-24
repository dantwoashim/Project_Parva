"""Temporal Compass API for cockpit-style home route."""

from __future__ import annotations

from fastapi import APIRouter, Query
from typing import Optional

from app.explainability import create_reason_trace
from app.services import build_temporal_compass

from ._personal_utils import base_meta_payload, normalize_coordinates, normalize_timezone, parse_date

router = APIRouter(prefix="/api/temporal", tags=["temporal"])


@router.get("/compass")
async def temporal_compass(
    date_str: str = Query(..., alias="date", description="Gregorian date in YYYY-MM-DD format"),
    lat: Optional[str] = Query(None, description="Latitude"),
    lon: Optional[str] = Query(None, description="Longitude"),
    tz: Optional[str] = Query("Asia/Kathmandu", description="IANA timezone"),
    quality_band: str = Query("computed", description="computed|provisional|inventory|all"),
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
        inputs={"date": target_date.isoformat(), "lat": latitude, "lon": longitude, "tz": timezone_name},
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

    return {
        **payload,
        "warnings": coord_warnings + tz_warnings,
        **base_meta_payload(
            trace_id=trace["trace_id"],
            confidence="computed",
            method="ephemeris_udaya",
            method_profile="temporal_compass_v1",
            quality_band="validated",
            assumption_set_id="np-mainstream-v2",
            advisory_scope="informational",
        ),
    }
