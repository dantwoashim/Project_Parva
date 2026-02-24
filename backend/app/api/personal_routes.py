"""Personal Panchanga APIs (v3 public profile)."""

from __future__ import annotations

from fastapi import APIRouter, Query
from typing import Optional

from app.calendar.bikram_sambat import (
    get_bs_confidence,
    get_bs_estimated_error_days,
    get_bs_month_name,
    get_bs_source_range,
    gregorian_to_bs,
)
from app.calendar.panchanga import get_panchanga
from app.explainability import create_reason_trace
from app.uncertainty import build_bs_uncertainty, build_panchanga_uncertainty

from ._personal_utils import base_meta_payload, normalize_coordinates, normalize_timezone, parse_date

router = APIRouter(prefix="/api/personal", tags=["personal"])


@router.get("/panchanga")
async def personal_panchanga(
    date_str: str = Query(..., alias="date", description="Gregorian date in YYYY-MM-DD format"),
    lat: Optional[str] = Query(None, description="Latitude"),
    lon: Optional[str] = Query(None, description="Longitude"),
    tz: Optional[str] = Query("Asia/Kathmandu", description="IANA timezone, e.g. Asia/Kathmandu"),
):
    target_date = parse_date(date_str)
    latitude, longitude, coord_warnings = normalize_coordinates(lat, lon)
    timezone_name, tz_warnings = normalize_timezone(tz)
    timezone_source = "user_input" if tz and tz.strip() and timezone_name == tz.strip() else "fallback_default"

    panchanga = get_panchanga(target_date, latitude=latitude, longitude=longitude)
    bs_year, bs_month, bs_day = gregorian_to_bs(target_date)

    payload = {
        "date": target_date.isoformat(),
        "location": {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone_name,
        },
        "bikram_sambat": {
            "year": bs_year,
            "month": bs_month,
            "day": bs_day,
            "month_name": get_bs_month_name(bs_month),
            "confidence": get_bs_confidence(target_date),
            "source_range": get_bs_source_range(target_date),
            "estimated_error_days": get_bs_estimated_error_days(target_date),
            "uncertainty": build_bs_uncertainty(
                get_bs_confidence(target_date),
                get_bs_estimated_error_days(target_date),
            ),
        },
        "tithi": {
            "number": panchanga["tithi"]["display_number"],
            "absolute": panchanga["tithi"]["number"],
            "name": panchanga["tithi"]["name"],
            "paksha": panchanga["tithi"]["paksha"],
            "progress": panchanga["tithi"]["progress"],
            "method": "ephemeris_udaya",
        },
        "nakshatra": panchanga["nakshatra"],
        "yoga": panchanga["yoga"],
        "karana": panchanga["karana"],
        "vaara": panchanga["vaara"],
        "sunrise": panchanga["sunrise"],
        "local_sunrise": panchanga.get("sunrise"),
        "local_sunset": panchanga.get("sunset"),
        "timezone_source": timezone_source,
        "ephemeris": {
            "mode": panchanga.get("mode", "swiss_moshier"),
            "accuracy": panchanga.get("accuracy", "arcsecond"),
            "library": panchanga.get("library", "pyswisseph"),
        },
        "uncertainty": build_panchanga_uncertainty(),
        "warnings": coord_warnings + tz_warnings,
    }

    trace = create_reason_trace(
        trace_type="personal_panchanga",
        subject={"date": target_date.isoformat()},
        inputs={
            "date": target_date.isoformat(),
            "lat": latitude,
            "lon": longitude,
            "tz": timezone_name,
        },
        outputs={
            "bs": f"{bs_year}-{bs_month}-{bs_day}",
            "tithi": payload["tithi"]["name"],
            "nakshatra": payload["nakshatra"]["name"],
            "vaara": payload["vaara"]["name_english"],
        },
        steps=[
            {"step": "sunrise", "detail": "Calculated sunrise at provided coordinates."},
            {"step": "panchanga", "detail": "Derived tithi/nakshatra/yoga/karana/vaara from ephemeris."},
            {"step": "bs_conversion", "detail": "Converted Gregorian date to Bikram Sambat."},
        ],
    )

    return {
        **payload,
        **base_meta_payload(
            trace_id=trace["trace_id"],
            confidence="computed",
            method="ephemeris_udaya",
            method_profile="personal_panchanga_v2_udaya",
            quality_band="gold",
            assumption_set_id="np-personal-panchanga-v2",
            advisory_scope="ritual_planning",
        ),
    }
