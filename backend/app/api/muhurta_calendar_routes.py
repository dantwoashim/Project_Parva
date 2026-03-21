"""Calendar-first muhurta ranking API."""

from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.explainability import create_reason_trace
from app.services import build_muhurta_calendar

from ._personal_utils import (
    base_meta_payload,
    normalize_coordinates,
    normalize_timezone,
)

router = APIRouter(prefix="/api/muhurta", tags=["muhurta"])


@router.get("/calendar")
async def muhurta_calendar(
    from_date: date = Query(..., alias="from", description="Start date YYYY-MM-DD"),
    to_date: date = Query(..., alias="to", description="End date YYYY-MM-DD"),
    lat: Optional[str] = Query(None, description="Latitude"),
    lon: Optional[str] = Query(None, description="Longitude"),
    tz: Optional[str] = Query("Asia/Kathmandu", description="IANA timezone"),
    ceremony_type: str = Query(
        "general",
        alias="type",
        description="creative_focus|vivah|griha_pravesh|travel|upanayana|general",
    ),
    assumption_set: str = Query("np-mainstream-v2"),
):
    latitude, longitude, coord_warnings = normalize_coordinates(lat, lon)
    timezone_name, tz_warnings = normalize_timezone(tz)

    try:
        payload = build_muhurta_calendar(
            from_date=from_date,
            to_date=to_date,
            latitude=latitude,
            longitude=longitude,
            timezone_name=timezone_name,
            ceremony_type=ceremony_type,
            assumption_set=assumption_set,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    trace = create_reason_trace(
        trace_type="muhurta_calendar",
        subject={"from": from_date.isoformat(), "to": to_date.isoformat(), "type": ceremony_type},
        inputs={
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
            "lat": latitude,
            "lon": longitude,
            "tz": timezone_name,
            "type": ceremony_type,
            "assumption_set": assumption_set,
        },
        outputs={"days": payload.get("total", 0)},
        steps=[
            {"step": "date_range", "detail": "Expanded the requested planning window into daily candidates."},
            {"step": "daily_rank", "detail": "Ranked auspicious windows for each date in the range."},
            {"step": "summary", "detail": "Selected the best daily window and caution periods per date."},
        ],
    )

    return {
        **payload,
        "warnings": [*coord_warnings, *tz_warnings],
        **base_meta_payload(
            trace_id=trace["trace_id"],
            confidence="computed",
            method="muhurta_calendar_ranking",
            method_profile="muhurta_calendar_v1",
            quality_band="validated",
            assumption_set_id=payload.get("assumption_set_id", assumption_set),
            advisory_scope="ritual_planning",
        ),
    }


__all__ = ["router"]
