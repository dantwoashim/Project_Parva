"""Timeline endpoint for ribbon-style festival explorer."""

from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.explainability import create_reason_trace
from app.services.timeline_service import build_festival_timeline

from ._personal_utils import base_meta_payload

router = APIRouter(prefix="/api/festivals", tags=["festivals"])


@router.get("/timeline")
async def festivals_timeline(
    from_date: date = Query(..., alias="from", description="Start date YYYY-MM-DD"),
    to_date: date = Query(..., alias="to", description="End date YYYY-MM-DD"),
    quality_band: str = Query("computed", description="computed|provisional|inventory|all"),
    category: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Search by festival name/description"),
    lang: str = Query("en", description="en|ne"),
    sort: str = Query("chronological", description="chronological|recommended|popular|upcoming"),
):
    try:
        timeline = build_festival_timeline(
            from_date=from_date,
            to_date=to_date,
            quality_band=quality_band,
            category=category,
            region=region,
            search=search,
            lang=lang,
            sort=sort,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    trace = create_reason_trace(
        trace_type="festival_timeline",
        subject={"from": from_date.isoformat(), "to": to_date.isoformat()},
        inputs={
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
            "quality_band": quality_band,
            "category": category,
            "region": region,
            "search": search,
            "lang": lang,
            "sort": sort,
        },
        outputs={
            "groups": len(timeline.get("groups", [])),
            "items": timeline.get("total", 0),
            "facets": bool(timeline.get("facets")),
            "unresolved_matches": len(timeline.get("unresolved_matches", [])),
        },
        steps=[
            {
                "step": "resolve_window",
                "detail": "Loaded computed upcoming festivals in the selected date window.",
            },
            {"step": "filter", "detail": "Applied quality/category/region constraints."},
            {
                "step": "truth_state",
                "detail": "Captured matched observances that still lack resolved live dates for the requested window.",
            },
            {"step": "facet_counting", "detail": "Computed category, month, and region facet counts for desktop browse controls."},
            {"step": "group", "detail": "Grouped items by month for ribbon rendering."},
        ],
    )

    return {
        **timeline,
        **base_meta_payload(
            trace_id=trace["trace_id"],
            confidence="computed",
            method="festival_timeline_grouping",
            method_profile="festival_timeline_v1",
            quality_band="validated",
            assumption_set_id="np-festival-ribbon-v1",
            advisory_scope="informational",
        ),
    }
