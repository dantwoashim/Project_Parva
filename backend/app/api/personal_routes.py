"""Personal Panchanga APIs (v3 public profile)."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.core.request_context import CoordinateInput
from app.services.personal_surface_service import (
    build_personal_context_response,
    build_personal_panchanga_response,
    build_personal_proof_capsule,
)

router = APIRouter(prefix="/api/personal", tags=["personal"])


class PersonalPanchangaRequest(BaseModel):
    date: str = Field(..., description="Gregorian date in YYYY-MM-DD format")
    lat: CoordinateInput = Field(None, description="Latitude")
    lon: CoordinateInput = Field(None, description="Longitude")
    tz: Optional[str] = Field(None, description="IANA timezone")
    risk_mode: str = Field("standard", description="standard|strict")


@router.get("/panchanga")
async def personal_panchanga(
    date_str: str = Query(..., alias="date", description="Gregorian date in YYYY-MM-DD format"),
    lat: Optional[str] = Query(None, description="Latitude"),
    lon: Optional[str] = Query(None, description="Longitude"),
    tz: Optional[str] = Query(None, description="IANA timezone, e.g. Asia/Kathmandu"),
    risk_mode: str = Query("standard", description="standard|strict"),
):
    return build_personal_panchanga_response(
        date_str=date_str,
        lat=lat,
        lon=lon,
        tz=tz,
        risk_mode=risk_mode,
    )


@router.post("/panchanga")
async def personal_panchanga_post(payload: PersonalPanchangaRequest):
    return build_personal_panchanga_response(
        date_str=payload.date,
        lat=payload.lat,
        lon=payload.lon,
        tz=payload.tz,
        risk_mode=payload.risk_mode,
    )


@router.get("/panchanga/proof-capsule")
async def personal_panchanga_proof_capsule(
    date_str: str = Query(..., alias="date", description="Gregorian date in YYYY-MM-DD format"),
    lat: Optional[str] = Query(None, description="Latitude"),
    lon: Optional[str] = Query(None, description="Longitude"),
    tz: Optional[str] = Query(None, description="IANA timezone, e.g. Asia/Kathmandu"),
    risk_mode: str = Query("strict", description="standard|strict"),
):
    payload = build_personal_panchanga_response(
        date_str=date_str,
        lat=lat,
        lon=lon,
        tz=tz,
        risk_mode=risk_mode,
    )
    return build_personal_proof_capsule(
        surface="personal_panchanga",
        payload=payload,
        request={"date": date_str, "lat": lat, "lon": lon, "tz": tz, "risk_mode": risk_mode},
    )


@router.post("/panchanga/proof-capsule")
async def personal_panchanga_proof_capsule_post(payload: PersonalPanchangaRequest):
    response_payload = build_personal_panchanga_response(
        date_str=payload.date,
        lat=payload.lat,
        lon=payload.lon,
        tz=payload.tz,
        risk_mode=payload.risk_mode,
    )
    return build_personal_proof_capsule(
        surface="personal_panchanga",
        payload=response_payload,
        request={
            "date": payload.date,
            "lat": payload.lat,
            "lon": payload.lon,
            "tz": payload.tz,
            "risk_mode": payload.risk_mode,
        },
    )


@router.get("/context")
async def personal_context(
    date_str: str = Query(..., alias="date", description="Gregorian date in YYYY-MM-DD format"),
    lat: Optional[str] = Query(None, description="Latitude"),
    lon: Optional[str] = Query(None, description="Longitude"),
    tz: Optional[str] = Query(None, description="IANA timezone, e.g. Asia/Kathmandu"),
    risk_mode: str = Query("standard", description="standard|strict"),
):
    return build_personal_context_response(
        date_str=date_str,
        lat=lat,
        lon=lon,
        tz=tz,
        risk_mode=risk_mode,
    )


@router.post("/context")
async def personal_context_post(payload: PersonalPanchangaRequest):
    return build_personal_context_response(
        date_str=payload.date,
        lat=payload.lat,
        lon=payload.lon,
        tz=payload.tz,
        risk_mode=payload.risk_mode,
    )


@router.get("/context/proof-capsule")
async def personal_context_proof_capsule(
    date_str: str = Query(..., alias="date", description="Gregorian date in YYYY-MM-DD format"),
    lat: Optional[str] = Query(None, description="Latitude"),
    lon: Optional[str] = Query(None, description="Longitude"),
    tz: Optional[str] = Query(None, description="IANA timezone, e.g. Asia/Kathmandu"),
    risk_mode: str = Query("strict", description="standard|strict"),
):
    payload = build_personal_context_response(
        date_str=date_str,
        lat=lat,
        lon=lon,
        tz=tz,
        risk_mode=risk_mode,
    )
    return build_personal_proof_capsule(
        surface="personal_context",
        payload=payload,
        request={"date": date_str, "lat": lat, "lon": lon, "tz": tz, "risk_mode": risk_mode},
    )


@router.post("/context/proof-capsule")
async def personal_context_proof_capsule_post(payload: PersonalPanchangaRequest):
    response_payload = build_personal_context_response(
        date_str=payload.date,
        lat=payload.lat,
        lon=payload.lon,
        tz=payload.tz,
        risk_mode=payload.risk_mode,
    )
    return build_personal_proof_capsule(
        surface="personal_context",
        payload=response_payload,
        request={
            "date": payload.date,
            "lat": payload.lat,
            "lon": payload.lon,
            "tz": payload.tz,
            "risk_mode": payload.risk_mode,
        },
    )
