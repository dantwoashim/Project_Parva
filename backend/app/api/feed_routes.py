"""iCal feed endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query, Request

from app.api.feed_service import (
    build_catalog_response,
    build_feed_manifest,
    build_feed_response,
    build_preview_response,
    split_csv,
)

router = APIRouter(prefix="/api/feeds", tags=["feeds"])


@router.get("/integrations/catalog")
async def feed_integrations_catalog(
    request: Request,
    years: int = Query(2, ge=1, le=10),
    start_year: Optional[int] = Query(None, ge=1900, le=2300),
    lang: str = Query("en"),
):
    return build_catalog_response(
        request=request,
        years=years,
        start_year=start_year,
        lang=lang,
        route_names={
            "all": "feed_all_ics",
            "national": "feed_national_ics",
            "newari": "feed_newari_ics",
        },
        platform_variant="rich",
    )


@router.get("/integrations/custom-plan")
async def feed_integrations_custom_plan(
    request: Request,
    festivals: str = Query(..., description="Comma-separated festival ids"),
    years: int = Query(2, ge=1, le=10),
    start_year: Optional[int] = Query(None, ge=1900, le=2300),
    lang: str = Query("en"),
):
    festival_ids = split_csv(festivals)
    return build_feed_manifest(
        key="custom",
        title="Custom Calendar",
        description="Only the observances you selected, packaged for Apple Calendar, Google Calendar, and direct ICS use.",
        request=request,
        route_name="feed_custom_ics",
        years=years,
        lang=lang,
        start_year=start_year,
        festivals=festival_ids,
        platform_actions=True,
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
    fest_ids = split_csv(festivals) or None
    name = "Project Parva Feed"
    if category:
        name = f"Project Parva {category.title()}"
    elif fest_ids:
        name = "Project Parva Custom"

    return build_feed_response(
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
    return build_feed_response(
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
    return build_feed_response(
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
    return build_feed_response(
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
    fest_ids = split_csv(festivals)
    return build_feed_response(
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
    return build_preview_response(days=days, lang=lang)
