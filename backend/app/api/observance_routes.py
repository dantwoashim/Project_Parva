"""Cross-calendar observance resolver endpoints."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.observances import resolve_observances


router = APIRouter(prefix="/api/observances", tags=["observances"])
PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFLICTS_PATH = PROJECT_ROOT / "data" / "cross_calendar" / "conflicts.json"


def _parse_csv(raw: Optional[str]) -> List[str]:
    return [p.strip().lower() for p in (raw or "").split(",") if p.strip()]


def _filter_by_calendars(rows: list[dict], calendars: list[str]) -> list[dict]:
    if not calendars:
        return rows
    allowed = set(calendars)
    return [row for row in rows if str(row.get("calendar_family", "")).lower() in allowed]


@router.get("")
async def resolve_observances_route(
    target_date: date = Query(..., alias="date", description="Date in YYYY-MM-DD"),
    location: str = Query("kathmandu", description="Context location (city/country)"),
    preferences: Optional[str] = Query(
        None,
        description="Comma-separated calendar preferences, e.g. nepali_hindu,islamic",
    ),
):
    """Resolve and rank observances across loaded calendar families."""
    pref_list = _parse_csv(preferences)
    ranked = resolve_observances(target_date, location=location, preferences=pref_list)

    return {
        "date": target_date.isoformat(),
        "location": location,
        "preferences": pref_list,
        "count": len(ranked),
        "has_conflicts": len(ranked) > 1,
        "observances": ranked,
    }


@router.get("/today")
async def resolve_today(
    location: str = Query("kathmandu"),
    preferences: Optional[str] = Query(None),
):
    today = date.today()
    return await resolve_observances_route(
        target_date=today,
        location=location,
        preferences=preferences,
    )


@router.get("/next")
async def next_observance(
    from_date: Optional[date] = Query(None, description="Start date YYYY-MM-DD (defaults to today)"),
    days: int = Query(30, ge=1, le=365, description="Search horizon in days"),
    location: str = Query("kathmandu"),
    preferences: Optional[str] = Query(None, description="Comma-separated calendar preferences"),
    calendars: Optional[str] = Query(
        None, description="Optional calendar family filter, e.g. nepali_hindu,islamic"
    ),
):
    """
    Return the next resolved observance from a start date over a look-ahead window.
    """
    start = from_date or date.today()
    pref_list = _parse_csv(preferences)
    calendar_list = _parse_csv(calendars)

    for offset in range(days + 1):
        probe = start + timedelta(days=offset)
        ranked = resolve_observances(probe, location=location, preferences=pref_list)
        ranked = _filter_by_calendars(ranked, calendar_list)
        if ranked:
            return {
                "from_date": start.isoformat(),
                "resolved_date": probe.isoformat(),
                "days_ahead": offset,
                "location": location,
                "preferences": pref_list,
                "calendars": calendar_list,
                "top_observance": ranked[0],
                "observances": ranked,
            }

    raise HTTPException(
        status_code=404,
        detail=f"No observance found within {days} days from {start.isoformat()}",
    )


@router.get("/stream")
async def observance_stream(
    start: Optional[date] = Query(None, description="Start date YYYY-MM-DD"),
    days: int = Query(7, ge=1, le=30, description="Number of days to include"),
    location: str = Query("kathmandu"),
    preferences: Optional[str] = Query(None),
    calendars: Optional[str] = Query(None),
):
    """
    Poll-style stream endpoint for clients that do periodic syncs instead of webhooks.
    """
    begin = start or date.today()
    pref_list = _parse_csv(preferences)
    calendar_list = _parse_csv(calendars)

    out: list[dict] = []
    for offset in range(days):
        probe = begin + timedelta(days=offset)
        ranked = resolve_observances(probe, location=location, preferences=pref_list)
        ranked = _filter_by_calendars(ranked, calendar_list)
        out.append(
            {
                "date": probe.isoformat(),
                "count": len(ranked),
                "top_observance": ranked[0] if ranked else None,
                "observances": ranked,
            }
        )

    return {
        "start": begin.isoformat(),
        "days": days,
        "location": location,
        "preferences": pref_list,
        "calendars": calendar_list,
        "results": out,
    }


@router.get("/conflicts")
async def get_conflict_dataset():
    """Return curated cross-calendar conflict scenarios."""
    if not CONFLICTS_PATH.exists():
        raise HTTPException(status_code=404, detail="Conflict dataset not found")
    payload = json.loads(CONFLICTS_PATH.read_text(encoding="utf-8"))
    return payload
