"""Integration-facing feed aliases for /api/integrations/feeds/*."""

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

router = APIRouter(prefix="/api/integrations/feeds", tags=["integrations"])


@router.get("/catalog")
async def integration_feed_catalog(
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
            "all": "all_feed",
            "national": "national_feed",
            "newari": "newari_feed",
        },
        platform_variant="compact",
    )


@router.get("/custom-plan")
async def integration_custom_feed_catalog(
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
        route_name="custom_feed",
        years=years,
        lang=lang,
        start_year=start_year,
        festivals=festival_ids,
        platform_actions=False,
    )


@router.get("/all.ics")
async def all_feed(
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
async def national_feed(
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
async def newari_feed(
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
async def custom_feed(
    request: Request,
    festivals: str = Query(..., description="Comma-separated festival ids"),
    years: int = Query(2, ge=1, le=10),
    start_year: Optional[int] = Query(None, ge=1900, le=2300),
    lang: str = Query("en"),
    download: bool = Query(False),
):
    return build_feed_response(
        request=request,
        festivals=split_csv(festivals),
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
    return build_preview_response(days=days, lang=lang)
