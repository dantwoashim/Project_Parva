"""iCal feed endpoints."""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Query, Request
from fastapi.responses import PlainTextResponse

from app.integrations import build_ical_feed, collect_feed_events

router = APIRouter(prefix="/api/feeds", tags=["feeds"])


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
    first_event = events[0] if events else None
    last_event = events[-1] if events else None
    upcoming = next((event for event in events if event.end_date >= today), None)
    highlights = []

    for event in events:
        if len(highlights) >= 3:
            break
        if any(existing["summary"] == event.summary for existing in highlights):
            continue
        highlights.append(
            {
                "summary": event.summary,
                "start_date": event.start_date.isoformat(),
                "end_date": event.end_date.isoformat(),
            }
        )

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
        "highlights": highlights,
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
    stats = _summarize_events(events)
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
                "action": "open_subscription",
            },
            "google": {
                "open_url": "https://calendar.google.com/calendar/u/0/r/settings/addbyurl",
                "copy_url": feed_url,
                "download_url": download_url,
                "action": "copy_then_open",
            },
            "manual": {
                "open_url": download_url,
                "copy_url": feed_url,
                "download_url": download_url,
                "action": "copy_or_download",
            },
        },
        "stats": stats,
        "years": years,
        "lang": lang,
        "start_year": start_year or date.today().year,
        "selection_count": len(festivals or []),
        "festival_ids": festivals or [],
        "is_custom": bool(festivals),
    }


def _build_feed_response(
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
    source_url = str(request.url.replace(query=request.url.query))
    body = build_ical_feed(
        calendar_name=calendar_name,
        events=events,
        description=f"{calendar_name} ({len(events)} events)",
        source_url=source_url,
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


@router.get("/integrations/catalog")
async def feed_integrations_catalog(
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
            route_name="feed_all_ics",
            years=years,
            lang=lang,
            start_year=start_year,
        ),
        _build_feed_manifest(
            key="national",
            title="National Holidays",
            description="A lighter calendar focused on major public observances.",
            request=request,
            route_name="feed_national_ics",
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
            route_name="feed_newari_ics",
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
                "badge": "One tap on Apple devices",
                "supports_webcal": True,
                "recommended_action": "Open the subscription link directly on iPhone, iPad, or Mac.",
                "cta_label": "Open in Apple Calendar",
                "copy_label": "Copy Apple subscription link",
                "sync_expectation": "Subscribed calendars usually refresh automatically after you confirm the subscription.",
                "best_for": ["iPhone", "iPad", "Mac"],
                "steps": [
                    "Tap the Apple button.",
                    "Confirm subscription when Calendar opens.",
                    "Choose refresh options inside Calendar if needed.",
                ],
            },
            "google": {
                "title": "Google Calendar",
                "badge": "Copy first, then paste on desktop",
                "supports_webcal": False,
                "recommended_action": "Copy the feed URL, then add it from URL in Google Calendar on a computer browser.",
                "cta_label": "Copy link and open Google Calendar",
                "copy_label": "Copy Google feed link",
                "sync_expectation": "Google Calendar subscriptions can take several hours to refresh after you add the URL.",
                "best_for": ["Chrome", "desktop browser", "Google Workspace accounts"],
                "steps": [
                    "Copy the feed link.",
                    "Open Google Calendar on a computer.",
                    "Use Other calendars > From URL and paste the link.",
                ],
                "requires_desktop": True,
            },
            "manual": {
                "title": "Any calendar app",
                "badge": "Direct feed or ICS file",
                "supports_webcal": True,
                "recommended_action": "Use the direct HTTPS feed or download the ICS file.",
                "cta_label": "Download .ics",
                "copy_label": "Copy direct link",
                "sync_expectation": "Manual imports are best when you need Outlook, Fantastical, or another calendar app.",
            },
        },
        "presets": presets,
    }


@router.get("/integrations/custom-plan")
async def feed_integrations_custom_plan(
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
        route_name="feed_custom_ics",
        years=years,
        lang=lang,
        start_year=start_year,
        festivals=festival_ids,
    )


@router.get("/ical")
async def feed_ical(
    request: Request,
    festivals: Optional[str] = Query(None, description="Comma-separated festival ids"),
    category: Optional[str] = Query(None, description="Festival category filter"),
    years: int = Query(2, ge=1, le=10),
    start_year: Optional[int] = Query(None, ge=1900, le=2300),
    lang: str = Query("en", description="en or ne"),
    download: bool = Query(False),
):
    fest_ids = _split_csv(festivals) or None
    name = "Project Parva Feed"
    if category:
        name = f"Project Parva {category.title()}"
    elif fest_ids:
        name = "Project Parva Custom"

    return _build_feed_response(
        request=request,
        festivals=fest_ids,
        category=category,
        years=years,
        lang=lang,
        calendar_name=name,
        filename="parva.ics",
        start_year=start_year,
        download=download,
    )


@router.get("/all.ics")
async def feed_all_ics(
    request: Request,
    years: int = Query(2, ge=1, le=10),
    start_year: Optional[int] = Query(None, ge=1900, le=2300),
    lang: str = Query("en"),
    download: bool = Query(False),
):
    return _build_feed_response(
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
async def feed_national_ics(
    request: Request,
    years: int = Query(2, ge=1, le=10),
    start_year: Optional[int] = Query(None, ge=1900, le=2300),
    lang: str = Query("en"),
    download: bool = Query(False),
):
    return _build_feed_response(
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
async def feed_newari_ics(
    request: Request,
    years: int = Query(2, ge=1, le=10),
    start_year: Optional[int] = Query(None, ge=1900, le=2300),
    lang: str = Query("en"),
    download: bool = Query(False),
):
    return _build_feed_response(
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
async def feed_custom_ics(
    request: Request,
    festivals: str = Query(..., description="Comma-separated festival ids"),
    years: int = Query(2, ge=1, le=10),
    start_year: Optional[int] = Query(None, ge=1900, le=2300),
    lang: str = Query("en"),
    download: bool = Query(False),
):
    fest_ids = _split_csv(festivals)
    return _build_feed_response(
        request=request,
        festivals=fest_ids,
        category=None,
        years=years,
        lang=lang,
        calendar_name="Project Parva Custom Feed",
        filename="parva-custom.ics",
        start_year=start_year,
        download=download,
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
