"""Muhurta heatmap API."""

from __future__ import annotations

from fastapi import APIRouter, Query
from typing import Optional

from app.explainability import create_reason_trace
from app.services import build_muhurta_heatmap

from ._personal_utils import base_meta_payload, normalize_coordinates, normalize_timezone, parse_date

router = APIRouter(prefix="/api/muhurta", tags=["muhurta"])


@router.get("/heatmap")
async def muhurta_heatmap(
    date_str: str = Query(..., alias="date", description="Gregorian date in YYYY-MM-DD format"),
    lat: Optional[str] = Query(None, description="Latitude"),
    lon: Optional[str] = Query(None, description="Longitude"),
    tz: Optional[str] = Query("Asia/Kathmandu", description="IANA timezone"),
    ceremony_type: str = Query("general", alias="type", description="vivah|griha_pravesh|travel|upanayana|general"),
    assumption_set: str = Query("np-mainstream-v2"),
):
    target_date = parse_date(date_str)
    latitude, longitude, coord_warnings = normalize_coordinates(lat, lon)
    timezone_name, tz_warnings = normalize_timezone(tz)

    payload = build_muhurta_heatmap(
        target_date=target_date,
        latitude=latitude,
        longitude=longitude,
        timezone_name=timezone_name,
        ceremony_type=ceremony_type,
        assumption_set=assumption_set,
    )

    trace = create_reason_trace(
        trace_type="muhurta_heatmap",
        subject={"date": target_date.isoformat(), "type": ceremony_type},
        inputs={"date": target_date.isoformat(), "lat": latitude, "lon": longitude, "tz": timezone_name},
        outputs={
            "blocks": len(payload.get("blocks", [])),
            "best_window": (payload.get("best_window") or {}).get("name"),
        },
        steps=[
            {"step": "window_generation", "detail": "Generated day/night muhurta windows."},
            {"step": "ranking", "detail": "Applied ceremony profile and assumption set ranking."},
            {"step": "classification", "detail": "Classified windows into auspicious/neutral/avoid classes."},
        ],
    )

    return {
        **payload,
        "warnings": coord_warnings + tz_warnings,
        **base_meta_payload(
            trace_id=trace["trace_id"],
            confidence="computed",
            method="rule_ranked_muhurta_v2",
            method_profile="muhurta_heatmap_v1",
            quality_band="validated",
            assumption_set_id=payload.get("assumption_set_id", assumption_set),
            advisory_scope="ritual_planning",
        ),
    }
