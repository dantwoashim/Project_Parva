"""Integration-facing feed aliases for /api/integrations/feeds/*."""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Query
from fastapi.responses import PlainTextResponse

from app.integrations import build_ical_feed, collect_feed_events


router = APIRouter(prefix="/api/integrations/feeds", tags=["integrations"])


def _split_csv(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def _feed_response(
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


@router.get("/all.ics")
async def all_feed(
    years: int = Query(2, ge=1, le=10),
    start_year: Optional[int] = Query(None, ge=1900, le=2300),
    lang: str = Query("en"),
):
    return _feed_response(
        festivals=None,
        category=None,
        years=years,
        lang=lang,
        calendar_name="Project Parva All Festivals",
        filename="parva-all.ics",
        start_year=start_year,
    )


@router.get("/national.ics")
async def national_feed(
    years: int = Query(2, ge=1, le=10),
    start_year: Optional[int] = Query(None, ge=1900, le=2300),
    lang: str = Query("en"),
):
    return _feed_response(
        festivals=None,
        category="national",
        years=years,
        lang=lang,
        calendar_name="Project Parva National Holidays",
        filename="parva-national.ics",
        start_year=start_year,
    )


@router.get("/newari.ics")
async def newari_feed(
    years: int = Query(2, ge=1, le=10),
    start_year: Optional[int] = Query(None, ge=1900, le=2300),
    lang: str = Query("en"),
):
    return _feed_response(
        festivals=None,
        category="newari",
        years=years,
        lang=lang,
        calendar_name="Project Parva Newari Festivals",
        filename="parva-newari.ics",
        start_year=start_year,
    )


@router.get("/custom.ics")
async def custom_feed(
    festivals: str = Query(..., description="Comma-separated festival ids"),
    years: int = Query(2, ge=1, le=10),
    start_year: Optional[int] = Query(None, ge=1900, le=2300),
    lang: str = Query("en"),
):
    return _feed_response(
        festivals=_split_csv(festivals),
        category=None,
        years=years,
        lang=lang,
        calendar_name="Project Parva Custom Feed",
        filename="parva-custom.ics",
        start_year=start_year,
    )


@router.get("/next")
async def integration_feed_preview(
    days: int = Query(30, ge=1, le=365),
    lang: str = Query("en"),
):
    start = date.today()
    events = collect_feed_events(years=2, lang=lang)
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
