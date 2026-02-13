"""iCal feed generation utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Iterable, Sequence

from app.festivals.repository import get_repository


@dataclass
class FeedEvent:
    """All-day iCal event payload."""

    uid: str
    summary: str
    description: str
    start_date: date
    end_date: date
    categories: str
    location: str | None = None
    language: str = "en"


def _escape_ics(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
        .replace("\r", "")
    )


def _as_yyyymmdd(value: date) -> str:
    return value.strftime("%Y%m%d")


def _event_lines(event: FeedEvent, *, now_utc: datetime) -> list[str]:
    dtstamp = now_utc.strftime("%Y%m%dT%H%M%SZ")
    # All-day events use non-inclusive DTEND.
    dtend = event.end_date + timedelta(days=1)

    lines = [
        "BEGIN:VEVENT",
        f"UID:{_escape_ics(event.uid)}",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART;VALUE=DATE:{_as_yyyymmdd(event.start_date)}",
        f"DTEND;VALUE=DATE:{_as_yyyymmdd(dtend)}",
        f"SUMMARY;LANGUAGE={event.language}:{_escape_ics(event.summary)}",
        f"DESCRIPTION;LANGUAGE={event.language}:{_escape_ics(event.description)}",
        f"CATEGORIES:{_escape_ics(event.categories)}",
    ]
    if event.location:
        lines.append(f"LOCATION;LANGUAGE={event.language}:{_escape_ics(event.location)}")
    lines.append("END:VEVENT")
    return lines


def _resolve_language_name(festival, lang: str) -> str:
    if lang.lower() == "ne" and festival.name_nepali:
        return festival.name_nepali
    return festival.name


def _festival_location_name(festival) -> str | None:
    if not festival.locations:
        return None
    first = festival.locations[0]
    return first.name


def collect_feed_events(
    *,
    festival_ids: Sequence[str] | None = None,
    category: str | None = None,
    years: int = 2,
    start_year: int | None = None,
    lang: str = "en",
) -> list[FeedEvent]:
    """Collect event objects for iCal feed generation."""
    repo = get_repository()

    if festival_ids:
        festivals = [repo.get_by_id(fid) for fid in festival_ids]
        festivals = [f for f in festivals if f is not None]
    elif category:
        festivals = repo.get_by_category(category)
    else:
        festivals = repo.get_all()

    begin_year = start_year or date.today().year
    end_year = begin_year + max(years, 1)

    events: list[FeedEvent] = []

    for festival in festivals:
        for year in range(begin_year, end_year):
            dates = repo.get_dates(festival.id, year)
            if not dates:
                continue

            summary = _resolve_language_name(festival, lang)
            desc = festival.tagline or festival.description
            if festival.description and festival.description not in desc:
                desc = f"{desc}\n\n{festival.description}"

            events.append(
                FeedEvent(
                    uid=f"{festival.id}-{dates.start_date.isoformat()}@projectparva.local",
                    summary=summary,
                    description=desc,
                    start_date=dates.start_date,
                    end_date=dates.end_date,
                    categories=festival.category,
                    location=_festival_location_name(festival),
                    language="ne" if lang.lower() == "ne" else "en",
                )
            )

    events.sort(key=lambda e: (e.start_date, e.summary))
    return events


def build_ical_feed(
    *,
    calendar_name: str,
    events: Iterable[FeedEvent],
    description: str = "Project Parva Festival Feed",
) -> str:
    """Build iCal (.ics) string from event objects."""
    now_utc = datetime.now(timezone.utc)

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "PRODID:-//Project Parva//Festival Feed//EN",
        f"X-WR-CALNAME:{_escape_ics(calendar_name)}",
        f"X-WR-CALDESC:{_escape_ics(description)}",
    ]

    for event in events:
        lines.extend(_event_lines(event, now_utc=now_utc))

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"
