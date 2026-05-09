"""Narrow public-demo calendar routes for lightweight hosted previews."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.calendar_conversion_service import (
    build_bs_to_gregorian_payload,
    build_conversion_payload,
    parse_iso_date,
)
from app.services.calendar_surface_service import build_today_payload

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


class BSConversionRequest(BaseModel):
    year: int
    month: int
    day: int


@router.get("/today")
async def get_today(risk_mode: str = Query("standard", description="standard|strict")):
    return build_today_payload(risk_mode=risk_mode)


@router.get("/convert")
async def convert_date(
    date_str: str = Query(
        ...,
        alias="date",
        description="Gregorian date in YYYY-MM-DD format",
        examples={"default": {"summary": "Sample date", "value": "2026-04-14"}},
    )
):
    gregorian_date = parse_iso_date(date_str)
    return build_conversion_payload(gregorian_date)


@router.post("/bs-to-gregorian")
async def bs_to_gregorian_convert(request: BSConversionRequest):
    try:
        return build_bs_to_gregorian_payload(request.year, request.month, request.day)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/panchanga")
async def get_panchanga_endpoint(
    date_str: str | None = Query(
        None,
        alias="date",
        description="Gregorian date in YYYY-MM-DD format",
        examples={"default": {"summary": "Sample date", "value": "2026-04-14"}},
    ),
    risk_mode: str = Query("standard", description="standard|strict"),
):
    from app.services.calendar_surface_service import build_panchanga_payload

    target_date = parse_iso_date(date_str) if date_str else date.today()
    return build_panchanga_payload(target_date, risk_mode=risk_mode)


__all__ = ["router"]
