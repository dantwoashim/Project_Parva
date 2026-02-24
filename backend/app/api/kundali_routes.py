"""Kundali APIs (D1, D9, lagna, aspects, yogas/dosha, layered dasha)."""

from __future__ import annotations

from fastapi import APIRouter, Query
from typing import Optional

from app.calendar.kundali import compute_kundali
from app.explainability import create_reason_trace

from ._personal_utils import (
    base_meta_payload,
    normalize_coordinates,
    normalize_timezone,
    parse_datetime,
)

router = APIRouter(prefix="/api/kundali", tags=["kundali"])


def _build_insight_blocks(kundali: dict) -> list[dict]:
    moon = (kundali.get("grahas") or {}).get("moon", {})
    lagna = kundali.get("lagna") or {}
    aspects = kundali.get("aspects") or []
    yogas = kundali.get("yogas") or []
    doshas = kundali.get("doshas") or []

    blocks = [
        {
            "id": "identity_axis",
            "title": "Identity Axis",
            "summary": (
                f"Lagna in {lagna.get('rashi_english', 'unknown')} and Moon in "
                f"{moon.get('rashi_english', 'unknown')} shape core temperament signals."
            ),
            "severity": "info",
        },
        {
            "id": "aspect_network",
            "title": "Aspect Network",
            "summary": f"Detected {len(aspects)} major aspects across graha placements.",
            "severity": "info",
        },
    ]

    if yogas:
        blocks.append(
            {
                "id": "yoga_highlights",
                "title": "Yoga Highlights",
                "summary": ", ".join(str(row.get("id", "Yoga")) for row in yogas[:4]),
                "severity": "positive",
            }
        )

    if doshas:
        blocks.append(
            {
                "id": "dosha_flags",
                "title": "Dosha Flags",
                "summary": ", ".join(str(row.get("id", "Dosha")) for row in doshas[:4]),
                "severity": "caution",
            }
        )

    return blocks


@router.get("")
async def kundali_endpoint(
    datetime_str: str = Query(..., alias="datetime", description="ISO8601 datetime"),
    lat: Optional[str] = Query(None, description="Latitude"),
    lon: Optional[str] = Query(None, description="Longitude"),
    tz: Optional[str] = Query("Asia/Kathmandu", description="IANA timezone"),
):
    latitude, longitude, coord_warnings = normalize_coordinates(lat, lon)
    timezone_name, tz_warnings = normalize_timezone(tz)
    birth_dt = parse_datetime(datetime_str, tz_name=timezone_name)

    kundali = compute_kundali(
        birth_dt,
        lat=latitude,
        lon=longitude,
        tz_name=timezone_name,
    )

    trace = create_reason_trace(
        trace_type="kundali",
        subject={"datetime": birth_dt.isoformat()},
        inputs={
            "datetime": birth_dt.isoformat(),
            "lat": latitude,
            "lon": longitude,
            "tz": timezone_name,
        },
        outputs={
            "lagna": kundali["lagna"],
            "graha_count": len(kundali["grahas"]),
            "house_count": len(kundali["houses"]),
            "aspect_count": len(kundali["aspects"]),
            "yoga_count": len(kundali["yogas"]),
            "dosha_count": len(kundali["doshas"]),
        },
        steps=[
            {"step": "graha_positions", "detail": "Calculated navagraha sidereal positions from Swiss Ephemeris."},
            {"step": "dignity_layer", "detail": "Assigned dignity state (exalted/own/neutral/debilitated) to each graha."},
            {"step": "aspects", "detail": "Computed Vedic graha drishti with orb-constrained strength scoring."},
            {"step": "yoga_dosha", "detail": "Evaluated yoga set v1 and dosha markers from D1 relations."},
            {"step": "dasha", "detail": "Built Vimshottari maha + antar dasha timeline."},
            {"step": "consistency", "detail": "Ran D1/D9/house consistency checks."},
        ],
    )

    advisory_notes = [
        "Kundali output is computational assistance, not a substitute for practitioner judgment.",
        "Yogas/doshas here are rule-based markers and may vary by school/tradition.",
    ]

    return {
        "datetime": birth_dt.isoformat(),
        "location": {"latitude": latitude, "longitude": longitude, "timezone": timezone_name},
        "lagna": kundali["lagna"],
        "grahas": kundali["grahas"],
        "houses": kundali["houses"],
        "d9": kundali["d9"],
        "aspects": kundali["aspects"],
        "yogas": kundali["yogas"],
        "doshas": kundali["doshas"],
        "dasha": kundali["dasha"],
        "consistency_checks": kundali["consistency_checks"],
        "insight_blocks": _build_insight_blocks(kundali),
        "advisory_notes": advisory_notes,
        "warnings": coord_warnings + tz_warnings,
        **base_meta_payload(
            trace_id=trace["trace_id"],
            confidence="computed",
            method="swiss_ephemeris_sidereal",
            method_profile="kundali_v2_aspects_dasha",
            quality_band="validated",
            assumption_set_id="np-kundali-v2",
            advisory_scope="astrology_assist",
        ),
    }


@router.get("/lagna")
async def lagna_endpoint(
    datetime_str: str = Query(..., alias="datetime", description="ISO8601 datetime"),
    lat: Optional[str] = Query(None, description="Latitude"),
    lon: Optional[str] = Query(None, description="Longitude"),
    tz: Optional[str] = Query("Asia/Kathmandu", description="IANA timezone"),
):
    latitude, longitude, coord_warnings = normalize_coordinates(lat, lon)
    timezone_name, tz_warnings = normalize_timezone(tz)
    birth_dt = parse_datetime(datetime_str, tz_name=timezone_name)

    kundali = compute_kundali(
        birth_dt,
        lat=latitude,
        lon=longitude,
        tz_name=timezone_name,
    )
    lagna = kundali["lagna"]

    trace = create_reason_trace(
        trace_type="kundali_lagna",
        subject={"datetime": birth_dt.isoformat()},
        inputs={
            "datetime": birth_dt.isoformat(),
            "lat": latitude,
            "lon": longitude,
            "tz": timezone_name,
        },
        outputs={"lagna": lagna},
        steps=[
            {"step": "ascendant", "detail": "Computed sidereal ascendant (lagna) using Swiss Ephemeris houses."},
        ],
    )

    return {
        "datetime": birth_dt.isoformat(),
        "location": {"latitude": latitude, "longitude": longitude, "timezone": timezone_name},
        "lagna": lagna,
        "warnings": coord_warnings + tz_warnings,
        **base_meta_payload(
            trace_id=trace["trace_id"],
            confidence="computed",
            method="swiss_ephemeris_lagna",
            method_profile="kundali_v2_aspects_dasha",
            quality_band="validated",
            assumption_set_id="np-kundali-v2",
            advisory_scope="astrology_assist",
        ),
    }
