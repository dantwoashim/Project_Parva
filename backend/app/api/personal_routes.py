"""Personal Panchanga APIs (v3 public profile)."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.core.request_context import CoordinateInput
from app.services import (
    build_personal_context_response,
    build_personal_panchanga_response,
)

router = APIRouter(prefix="/api/personal", tags=["personal"])


class PersonalPanchangaRequest(BaseModel):
    date: str = Field(..., description="Gregorian date in YYYY-MM-DD format")
    lat: CoordinateInput = Field(None, description="Latitude")
    lon: CoordinateInput = Field(None, description="Longitude")
    tz: Optional[str] = Field(None, description="IANA timezone")


@router.get("/panchanga")
async def personal_panchanga(
    date_str: str = Query(..., alias="date", description="Gregorian date in YYYY-MM-DD format"),
    lat: Optional[str] = Query(None, description="Latitude"),
    lon: Optional[str] = Query(None, description="Longitude"),
    tz: Optional[str] = Query(None, description="IANA timezone, e.g. Asia/Kathmandu"),
):
    return build_personal_panchanga_response(date_str=date_str, lat=lat, lon=lon, tz=tz)


@router.post("/panchanga")
async def personal_panchanga_post(payload: PersonalPanchangaRequest):
    return build_personal_panchanga_response(
        date_str=payload.date,
        lat=payload.lat,
        lon=payload.lon,
        tz=payload.tz,
    )


@router.get("/context")
async def personal_context(
    date_str: str = Query(..., alias="date", description="Gregorian date in YYYY-MM-DD format"),
    lat: Optional[str] = Query(None, description="Latitude"),
    lon: Optional[str] = Query(None, description="Longitude"),
    tz: Optional[str] = Query(None, description="IANA timezone, e.g. Asia/Kathmandu"),
):
    return build_personal_context_response(date_str=date_str, lat=lat, lon=lon, tz=tz)


@router.post("/context")
async def personal_context_post(payload: PersonalPanchangaRequest):
    return build_personal_context_response(
        date_str=payload.date,
        lat=payload.lat,
        lon=payload.lon,
        tz=payload.tz,
    )
