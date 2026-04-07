"""Festival response presenters.

These presenters keep route/use-case layers focused on orchestration while the
response contract stays centralized in one place.
"""

from __future__ import annotations

from datetime import date
from typing import Sequence

from .models import (
    CalendarDayFestivals,
    Festival,
    FestivalCalendarResponse,
    FestivalDateAvailability,
    FestivalDates,
    FestivalDetailCompleteness,
    FestivalDetailResponse,
    FestivalDisputeAtlasResponse,
    FestivalDisputeRecord,
    FestivalListResponse,
    FestivalSummary,
    UpcomingFestival,
    UpcomingFestivalsResponse,
)


def present_festival_list(
    *,
    festivals: Sequence[FestivalSummary],
    total: int,
    page: int,
    page_size: int,
    provenance,
) -> FestivalListResponse:
    return FestivalListResponse(
        festivals=list(festivals),
        total=total,
        page=page,
        page_size=page_size,
        provenance=provenance,
    )


def present_dispute_atlas(
    *,
    year: int,
    disputes: Sequence[FestivalDisputeRecord],
    truth_ladder: list[dict[str, str]],
    provenance,
) -> FestivalDisputeAtlasResponse:
    return FestivalDisputeAtlasResponse(
        year=year,
        total_items=len(disputes),
        truth_ladder=truth_ladder,
        disputes=list(disputes),
        provenance=provenance,
    )


def present_upcoming_festivals(
    *,
    festivals: Sequence[UpcomingFestival],
    from_date: date,
    to_date: date,
    provenance,
) -> UpcomingFestivalsResponse:
    return UpcomingFestivalsResponse(
        festivals=list(festivals),
        from_date=from_date,
        to_date=to_date,
        total=len(festivals),
        provenance=provenance,
    )


def present_festival_calendar(
    *,
    days: Sequence[CalendarDayFestivals],
    month: int,
    year: int,
    provenance,
) -> FestivalCalendarResponse:
    return FestivalCalendarResponse(
        days=list(days),
        month=month,
        year=year,
        provenance=provenance,
    )


def present_festival_detail(
    *,
    festival: Festival,
    dates: FestivalDates | None,
    date_availability: FestivalDateAvailability | None,
    nearby_festivals: Sequence[FestivalSummary] | None,
    completeness: FestivalDetailCompleteness | None,
    provenance,
) -> FestivalDetailResponse:
    return FestivalDetailResponse(
        festival=festival,
        dates=dates,
        date_availability=date_availability,
        nearby_festivals=list(nearby_festivals) if nearby_festivals else None,
        completeness=completeness,
        provenance=provenance,
    )
