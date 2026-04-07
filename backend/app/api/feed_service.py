"""Shared feed builders for canonical and alias route families."""

from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import Request
from fastapi.responses import PlainTextResponse

from app.integrations import build_ical_feed, collect_feed_events

_PRESET_CONFIGS = (
    {
        "key": "all",
        "title": "All Festivals",
        "description": "The broadest Parva calendar, good for most personal use.",
        "category": None,
    },
    {
        "key": "national",
        "title": "National Holidays",
        "description": "A lighter calendar focused on major public observances.",
        "category": "national",
    },
    {
        "key": "newari",
        "title": "Newari Festivals",
        "description": "A focused calendar for Kathmandu Valley and Newar observances.",
        "category": "newari",
    },
)

_RICH_PLATFORM_GUIDE = {
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
}

_COMPACT_PLATFORM_GUIDE = {
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
}


def split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def _feed_url(request: Request, route_name: str, **params: object) -> str:
    query = {
        key: value
        for key, value in params.items()
        if value is not None and value != ""
    }
    return str(request.url_for(route_name).include_query_params(**query))


def _webcal_url(url: str) -> str:
    if url.startswith("https://"):
        return "webcal://" + url[len("https://") :]
    if url.startswith("http://"):
        return "webcal://" + url[len("http://") :]
    return url


def _summarize_events(events: list[object], *, include_highlights: bool) -> dict[str, Any]:
    today = date.today()
    first_event = events[0] if events else None
    last_event = events[-1] if events else None
    upcoming = next((event for event in events if event.end_date >= today), None)
    payload = {
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

    if include_highlights:
        highlights: list[dict[str, str]] = []
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
        payload["highlights"] = highlights

    return payload


def build_feed_manifest(
    *,
    key: str,
    title: str,
    description: str,
    request: Request,
    route_name: str,
    years: int,
    lang: str,
    start_year: int | None,
    festivals: list[str] | None = None,
    category: str | None = None,
    platform_actions: bool,
) -> dict[str, Any]:
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
    platform_links = {
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
    }
    if platform_actions:
        platform_links["apple"]["action"] = "open_subscription"
        platform_links["google"]["action"] = "copy_then_open"
        platform_links["manual"]["action"] = "copy_or_download"

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
        "platform_links": platform_links,
        "stats": _summarize_events(events, include_highlights=platform_actions),
        "years": years,
        "lang": lang,
        "start_year": start_year or date.today().year,
        "selection_count": len(festivals or []),
        "festival_ids": festivals or [],
        "is_custom": bool(festivals),
    }


def build_catalog_response(
    *,
    request: Request,
    years: int,
    start_year: int | None,
    lang: str,
    route_names: dict[str, str],
    platform_variant: str,
) -> dict[str, Any]:
    platform_actions = platform_variant == "rich"
    presets = [
        build_feed_manifest(
            key=preset["key"],
            title=preset["title"],
            description=preset["description"],
            request=request,
            route_name=route_names[preset["key"]],
            years=years,
            lang=lang,
            start_year=start_year,
            category=preset["category"],
            platform_actions=platform_actions,
        )
        for preset in _PRESET_CONFIGS
    ]
    return {
        "generated_at": date.today().isoformat(),
        "years": years,
        "lang": lang,
        "platforms": _RICH_PLATFORM_GUIDE if platform_variant == "rich" else _COMPACT_PLATFORM_GUIDE,
        "presets": presets,
    }


def build_feed_response(
    *,
    request: Request,
    festivals: list[str] | None,
    category: str | None,
    years: int,
    lang: str,
    calendar_name: str,
    filename: str,
    start_year: int | None = None,
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


def build_preview_response(*, days: int, lang: str, years: int = 2) -> dict[str, Any]:
    start = date.today()
    events = collect_feed_events(years=years, lang=lang)
    window = [event for event in events if 0 <= (event.start_date - start).days <= days]
    return {
        "from": start.isoformat(),
        "days": days,
        "count": len(window),
        "events": [
            {
                "summary": event.summary,
                "start_date": event.start_date.isoformat(),
                "end_date": event.end_date.isoformat(),
                "categories": event.categories,
            }
            for event in window
        ],
    }
