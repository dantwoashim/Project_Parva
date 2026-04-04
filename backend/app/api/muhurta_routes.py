"""Muhurta APIs (daily windows, rahu kalam, ceremony-specific ranking)."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.core.request_context import CoordinateInput
from app.services.muhurta_surface_service import (
    build_auspicious_muhurta_response,
    build_muhurta_for_day_response,
    build_rahu_kalam_response,
)

router = APIRouter(prefix="/api/muhurta", tags=["muhurta"])


class MuhurtaDayRequest(BaseModel):
    date: str = Field(..., description="Gregorian date in YYYY-MM-DD format")
    lat: CoordinateInput = Field(None, description="Latitude")
    lon: CoordinateInput = Field(None, description="Longitude")
    tz: Optional[str] = Field("Asia/Kathmandu", description="IANA timezone")
    birth_nakshatra: Optional[str] = Field(
        None, description="Birth nakshatra name or number 1-27 (optional tara-bala)"
    )


class RahuKalamRequest(BaseModel):
    date: str = Field(..., description="Gregorian date in YYYY-MM-DD format")
    lat: CoordinateInput = Field(None, description="Latitude")
    lon: CoordinateInput = Field(None, description="Longitude")
    tz: Optional[str] = Field("Asia/Kathmandu", description="IANA timezone")


class AuspiciousMuhurtaRequest(BaseModel):
    date: str = Field(..., description="Gregorian date in YYYY-MM-DD format")
    type: str = Field(
        "general", description="creative_focus|vivah|griha_pravesh|travel|upanayana|general"
    )
    lat: CoordinateInput = Field(None, description="Latitude")
    lon: CoordinateInput = Field(None, description="Longitude")
    tz: Optional[str] = Field("Asia/Kathmandu", description="IANA timezone")
    birth_nakshatra: Optional[str] = Field(
        None, description="Birth nakshatra name or number 1-27"
    )
    assumption_set: str = Field(
        "np-mainstream-v2", description="np-mainstream-v2|diaspora-practical-v2"
    )


@router.get("")
async def muhurta_for_day(
    date_str: str = Query(..., alias="date", description="Gregorian date in YYYY-MM-DD format"),
    lat: Optional[str] = Query(None, description="Latitude"),
    lon: Optional[str] = Query(None, description="Longitude"),
    tz: Optional[str] = Query("Asia/Kathmandu", description="IANA timezone"),
    birth_nakshatra: Optional[str] = Query(
        None, description="Birth nakshatra name or number 1-27 (optional tara-bala)"
    ),
):
    return build_muhurta_for_day_response(
        date_str=date_str,
        lat=lat,
        lon=lon,
        tz=tz,
        birth_nakshatra=birth_nakshatra,
    )


@router.post("")
async def muhurta_for_day_post(payload: MuhurtaDayRequest):
    return build_muhurta_for_day_response(
        date_str=payload.date,
        lat=payload.lat,
        lon=payload.lon,
        tz=payload.tz,
        birth_nakshatra=payload.birth_nakshatra,
    )


@router.get("/rahu-kalam")
async def rahu_kalam(
    date_str: str = Query(..., alias="date", description="Gregorian date in YYYY-MM-DD format"),
    lat: Optional[str] = Query(None, description="Latitude"),
    lon: Optional[str] = Query(None, description="Longitude"),
    tz: Optional[str] = Query("Asia/Kathmandu", description="IANA timezone"),
):
    return build_rahu_kalam_response(date_str=date_str, lat=lat, lon=lon, tz=tz)


@router.post("/rahu-kalam")
async def rahu_kalam_post(payload: RahuKalamRequest):
    return build_rahu_kalam_response(
        date_str=payload.date,
        lat=payload.lat,
        lon=payload.lon,
        tz=payload.tz,
    )


@router.get("/auspicious")
async def auspicious_muhurta(
    date_str: str = Query(..., alias="date", description="Gregorian date in YYYY-MM-DD format"),
    ceremony_type: str = Query(
        "general", alias="type", description="creative_focus|vivah|griha_pravesh|travel|upanayana|general"
    ),
    lat: Optional[str] = Query(None, description="Latitude"),
    lon: Optional[str] = Query(None, description="Longitude"),
    tz: Optional[str] = Query("Asia/Kathmandu", description="IANA timezone"),
    birth_nakshatra: Optional[str] = Query(None, description="Birth nakshatra name or number 1-27"),
    assumption_set: str = Query(
        "np-mainstream-v2", description="np-mainstream-v2|diaspora-practical-v2"
    ),
):
    return build_auspicious_muhurta_response(
        date_str=date_str,
        ceremony_type=ceremony_type,
        lat=lat,
        lon=lon,
        tz=tz,
        birth_nakshatra=birth_nakshatra,
        assumption_set=assumption_set,
    )


@router.post("/auspicious")
async def auspicious_muhurta_post(payload: AuspiciousMuhurtaRequest):
    return build_auspicious_muhurta_response(
        date_str=payload.date,
        ceremony_type=payload.type,
        lat=payload.lat,
        lon=payload.lon,
        tz=payload.tz,
        birth_nakshatra=payload.birth_nakshatra,
        assumption_set=payload.assumption_set,
    )
