"""Narrow public-demo calendar routes for lightweight hosted previews."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from app.api._clock import request_civil_date
from app.core.clock import DEFAULT_CIVIL_TIMEZONE
from app.services.calendar_conversion_service import (
    build_bs_to_gregorian_payload,
    build_conversion_payload,
    parse_iso_date,
)
from app.services.calendar_surface_service import build_today_payload

from ._async_utils import run_cpu_bound

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


class BSConversionRequest(BaseModel):
    year: int
    month: int
    day: int


@router.get("/today")
async def get_today(
    request: Request,
    risk_mode: str = Query("standard", description="standard|strict"),
    tz: str = Query(DEFAULT_CIVIL_TIMEZONE, description="IANA timezone"),
):
    today = request_civil_date(request, tz)
    return build_today_payload(risk_mode=risk_mode, today=today, timezone_name=tz)


@router.get("/convert")
async def convert_date(
    date_str: str = Query(
        ...,
        alias="date",
        description="Gregorian date in YYYY-MM-DD format",
        openapi_examples={"default": {"summary": "Sample date", "value": "2026-04-14"}},
    )
):
    gregorian_date = parse_iso_date(date_str)
    return build_conversion_payload(gregorian_date)


@router.post("/bs-to-gregorian")
async def bs_to_gregorian_convert(payload: BSConversionRequest, request: Request):
    try:
        return build_bs_to_gregorian_payload(
            payload.year,
            payload.month,
            payload.day,
            settings=getattr(request.app.state, "settings", None),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/panchanga")
async def get_panchanga_endpoint(
    request: Request,
    date_str: str | None = Query(
        None,
        alias="date",
        description="Gregorian date in YYYY-MM-DD format",
        openapi_examples={"default": {"summary": "Sample date", "value": "2026-04-14"}},
    ),
    risk_mode: str = Query("standard", description="standard|strict"),
    tz: str = Query(DEFAULT_CIVIL_TIMEZONE, description="IANA timezone"),
):
    from app.services.calendar_surface_service import build_panchanga_payload

    target_date = parse_iso_date(date_str) if date_str else request_civil_date(request, tz)
    return await run_cpu_bound(
        build_panchanga_payload,
        target_date,
        risk_mode=risk_mode,
        timezone_name=tz,
    )


__all__ = ["router"]
