"""iCal feed endpoints."""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Query
from fastapi.responses import PlainTextResponse

from app.integrations import build_ical_feed, collect_feed_events


router = APIRouter(prefix="/api/feeds", tags=["feeds"])


def _split_csv(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def _build_feed_response(
    *,
    festivals: Optional[List[str]],
    category: Optional[str],
    years: int,
    lang: str,
    calendar_name: str,
    filename: str,
    start_year: Optional[int] = None,
) -> PlainTextResponse:
    events = collect_feed_events(
        festival_ids=festivals,
        category=category,
        years=years,
        start_year=start_year,
        lang=lang,
    )
    body = build_ical_feed(
        calendar_name=calendar_name,
        events=events,
        description=f"{calendar_name} ({len(events)} events)",
    )
    return PlainTextResponse(
        content=body,
        media_type="text/calendar; charset=utf-8",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.get("/ical")
async def feed_ical(
    festivals: Optional[str] = Query(None, description="Comma-separated festival ids"),
    category: Optional[str] = Query(None, description="Festival category filter"),
    years: int = Query(2, ge=1, le=10),
    start_year: Optional[int] = Query(None, ge=1900, le=2300),
    lang: str = Query("en", description="en or ne"),
):
    fest_ids = _split_csv(festivals) or None
    name = "Project Parva Feed"
    if category:
        name = f"Project Parva {category.title()}"
    elif fest_ids:
        name = "Project Parva Custom"

    return _build_feed_response(
        festivals=fest_ids,
        category=category,
        years=years,
        lang=lang,
        calendar_name=name,
        filename="parva.ics",
        start_year=start_year,
    )


@router.get("/all.ics")
async def feed_all_ics(
    years: int = Query(2, ge=1, le=10),
    start_year: Optional[int] = Query(None, ge=1900, le=2300),
    lang: str = Query("en"),
):
    return _build_feed_response(
        festivals=None,
        category=None,
        years=years,
        lang=lang,
        calendar_name="Project Parva All Festivals",
        filename="parva-all.ics",
        start_year=start_year,
    )


@router.get("/national.ics")
async def feed_national_ics(
    years: int = Query(2, ge=1, le=10),
    start_year: Optional[int] = Query(None, ge=1900, le=2300),
    lang: str = Query("en"),
):
    return _build_feed_response(
        festivals=None,
        category="national",
        years=years,
        lang=lang,
        calendar_name="Project Parva National Holidays",
        filename="parva-national.ics",
        start_year=start_year,
    )


@router.get("/newari.ics")
async def feed_newari_ics(
    years: int = Query(2, ge=1, le=10),
    start_year: Optional[int] = Query(None, ge=1900, le=2300),
    lang: str = Query("en"),
):
    return _build_feed_response(
        festivals=None,
        category="newari",
        years=years,
        lang=lang,
        calendar_name="Project Parva Newari Festivals",
        filename="parva-newari.ics",
        start_year=start_year,
    )


@router.get("/custom.ics")
async def feed_custom_ics(
    festivals: str = Query(..., description="Comma-separated festival ids"),
    years: int = Query(2, ge=1, le=10),
    start_year: Optional[int] = Query(None, ge=1900, le=2300),
    lang: str = Query("en"),
):
    fest_ids = _split_csv(festivals)
    return _build_feed_response(
        festivals=fest_ids,
        category=None,
        years=years,
        lang=lang,
        calendar_name="Project Parva Custom Feed",
        filename="parva-custom.ics",
        start_year=start_year,
    )


@router.get("/next")
async def next_observances_feed_preview(
    days: int = Query(30, ge=1, le=365),
    lang: str = Query("en"),
):
    """Small JSON preview helper for feed consumers."""
    start = date.today()
    end_year = start.year + 1
    events = collect_feed_events(years=end_year - start.year + 1, lang=lang)
    window = [e for e in events if 0 <= (e.start_date - start).days <= days]
    return {
        "from": start.isoformat(),
        "days": days,
        "count": len(window),
        "events": [
            {
                "summary": e.summary,
                "start_date": e.start_date.isoformat(),
                "end_date": e.end_date.isoformat(),
                "categories": e.categories,
            }
            for e in window
        ],
    }
