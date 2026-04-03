"""Integration-facing feed aliases for /api/integrations/feeds/*."""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Query, Request
from fastapi.responses import PlainTextResponse

from app.integrations import build_ical_feed, collect_feed_events

router = APIRouter(prefix="/api/integrations/feeds", tags=["integrations"])


def _split_csv(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def _feed_url(request: Request, path: str, **params: object) -> str:
    query = {
        key: value
        for key, value in params.items()
        if value is not None and value != ""
    }
    return str(request.url_for(path, **{}).include_query_params(**query))


def _webcal_url(url: str) -> str:
    if url.startswith("https://"):
        return "webcal://" + url[len("https://") :]
    if url.startswith("http://"):
        return "webcal://" + url[len("http://") :]
    return url


def _summarize_events(events: List[object]) -> dict:
    today = date.today()
    upcoming = next((event for event in events if event.end_date >= today), None)
    first_event = events[0] if events else None
    last_event = events[-1] if events else None
    return {
        "event_count": len(events),
        "date_window": {
            "start": first_event.start_date.isoformat(),
            "end": last_event.end_date.isoformat(),
        }
        if first_event and last_event
        else None,
        "next_event": {
            "summary": upcoming.summary,
            "start_date": upcoming.start_date.isoformat(),
            "end_date": upcoming.end_date.isoformat(),
        }
        if upcoming
        else None,
    }


def _build_feed_manifest(
    *,
    key: str,
    title: str,
    description: str,
    request: Request,
    route_name: str,
    years: int,
    lang: str,
    start_year: Optional[int],
    festivals: Optional[List[str]] = None,
    category: Optional[str] = None,
) -> dict:
    params = {"years": years, "lang": lang, "start_year": start_year}
    if festivals:
        params["festivals"] = ",".join(festivals)
    feed_url = _feed_url(request, route_name, **params)
    download_url = _feed_url(request, route_name, **(params | {"download": 1}))
    events = collect_feed_events(
        festival_ids=festivals,
        category=category,
        years=years,
        start_year=start_year,
        lang=lang,
    )
    return {
        "key": key,
        "title": title,
        "description": description,
        "category": category,
        "feed_url": feed_url,
        "download_url": download_url,
        "webcal_url": _webcal_url(feed_url),
        "google_copy_url": feed_url,
        "apple_subscribe_url": _webcal_url(feed_url),
        "platform_links": {
            "apple": {
                "open_url": _webcal_url(feed_url),
                "copy_url": feed_url,
                "download_url": download_url,
            },
            "google": {
                "open_url": "https://calendar.google.com/calendar/u/0/r/settings/addbyurl",
                "copy_url": feed_url,
                "download_url": download_url,
            },
            "manual": {
                "open_url": download_url,
                "copy_url": feed_url,
                "download_url": download_url,
            },
        },
        "stats": _summarize_events(events),
        "years": years,
        "lang": lang,
        "start_year": start_year or date.today().year,
        "selection_count": len(festivals or []),
        "festival_ids": festivals or [],
        "is_custom": bool(festivals),
    }


def _feed_response(
    *,
    request: Request,
    festivals: Optional[List[str]],
    category: Optional[str],
    years: int,
    lang: str,
    calendar_name: str,
    filename: str,
    start_year: Optional[int] = None,
    download: bool = False,
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
        source_url=str(request.url),
    )
    disposition = "attachment" if download else "inline"
    return PlainTextResponse(
        content=body,
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": f'{disposition}; filename="{filename}"',
            "Cache-Control": "public, max-age=900",
            "X-Parva-Calendar-Name": calendar_name,
        },
    )


@router.get("/catalog")
async def integration_feed_catalog(
    request: Request,
    years: int = Query(2, ge=1, le=10),
    start_year: Optional[int] = Query(None, ge=1900, le=2300),
    lang: str = Query("en"),
):
    presets = [
        _build_feed_manifest(
            key="all",
            title="All Festivals",
            description="The broadest Parva calendar, good for most personal use.",
            request=request,
            route_name="all_feed",
            years=years,
            lang=lang,
            start_year=start_year,
        ),
        _build_feed_manifest(
            key="national",
            title="National Holidays",
            description="A lighter calendar focused on major public observances.",
            request=request,
            route_name="national_feed",
            years=years,
            lang=lang,
            start_year=start_year,
            category="national",
        ),
        _build_feed_manifest(
            key="newari",
            title="Newari Festivals",
            description="A focused calendar for Kathmandu Valley and Newar observances.",
            request=request,
            route_name="newari_feed",
            years=years,
            lang=lang,
            start_year=start_year,
            category="newari",
        ),
    ]
    return {
        "generated_at": date.today().isoformat(),
        "years": years,
        "lang": lang,
        "platforms": {
            "apple": {
                "title": "Apple Calendar",
                "supports_webcal": True,
                "cta_label": "Open in Apple Calendar",
            },
            "google": {
                "title": "Google Calendar",
                "supports_webcal": False,
                "cta_label": "Copy link and open Google Calendar",
                "requires_desktop": True,
            },
            "manual": {
                "title": "Any calendar app",
                "supports_webcal": True,
                "cta_label": "Download .ics",
            },
        },
        "presets": presets,
    }


@router.get("/custom-plan")
async def integration_custom_feed_catalog(
    request: Request,
    festivals: str = Query(..., description="Comma-separated festival ids"),
    years: int = Query(2, ge=1, le=10),
    start_year: Optional[int] = Query(None, ge=1900, le=2300),
    lang: str = Query("en"),
):
    festival_ids = _split_csv(festivals)
    return _build_feed_manifest(
        key="custom",
        title="Custom Calendar",
        description="Only the observances you selected, packaged for Apple Calendar, Google Calendar, and direct ICS use.",
        request=request,
        route_name="custom_feed",
        years=years,
        lang=lang,
        start_year=start_year,
        festivals=festival_ids,
    )


@router.get("/all.ics")
async def all_feed(
    request: Request,
    years: int = Query(2, ge=1, le=10),
    start_year: Optional[int] = Query(None, ge=1900, le=2300),
    lang: str = Query("en"),
    download: bool = Query(False),
):
    return _feed_response(
        request=request,
        festivals=None,
        category=None,
        years=years,
        lang=lang,
        calendar_name="Project Parva All Festivals",
        filename="parva-all.ics",
        start_year=start_year,
        download=download,
    )


@router.get("/national.ics")
async def national_feed(
    request: Request,
    years: int = Query(2, ge=1, le=10),
    start_year: Optional[int] = Query(None, ge=1900, le=2300),
    lang: str = Query("en"),
    download: bool = Query(False),
):
    return _feed_response(
        request=request,
        festivals=None,
        category="national",
        years=years,
        lang=lang,
        calendar_name="Project Parva National Holidays",
        filename="parva-national.ics",
        start_year=start_year,
        download=download,
    )


@router.get("/newari.ics")
async def newari_feed(
    request: Request,
    years: int = Query(2, ge=1, le=10),
    start_year: Optional[int] = Query(None, ge=1900, le=2300),
    lang: str = Query("en"),
    download: bool = Query(False),
):
    return _feed_response(
        request=request,
        festivals=None,
        category="newari",
        years=years,
        lang=lang,
        calendar_name="Project Parva Newari Festivals",
        filename="parva-newari.ics",
        start_year=start_year,
        download=download,
    )


@router.get("/custom.ics")
async def custom_feed(
    request: Request,
    festivals: str = Query(..., description="Comma-separated festival ids"),
    years: int = Query(2, ge=1, le=10),
    start_year: Optional[int] = Query(None, ge=1900, le=2300),
    lang: str = Query("en"),
    download: bool = Query(False),
):
    return _feed_response(
        request=request,
        festivals=_split_csv(festivals),
        category=None,
        years=years,
        lang=lang,
        calendar_name="Project Parva Custom Feed",
        filename="parva-custom.ics",
        start_year=start_year,
        download=download,
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
