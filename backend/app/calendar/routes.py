"""
Calendar API Routes
===================

Endpoints for calendar conversion and tithi information.
"""

from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.calendar.bikram_sambat import get_bs_month_name
from app.services.calendar_surface_service import (
    build_bs_to_gregorian_payload,
    build_calendar_proof_capsule,
    build_compare_conversion_payload,
    build_conversion_payload,
    build_dual_month_payload,
    build_panchanga_payload,
    build_panchanga_range_payload,
    build_provenance,
    build_tithi_detail_payload,
    build_today_payload,
    build_upcoming_festivals_payload,
    parse_iso_date as service_parse_iso_date,
)

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


class BSDate(BaseModel):
    """Bikram Sambat date."""
    year: int
    month: int
    day: int
    month_name: str
    confidence: str
    source_range: Optional[str] = None
    estimated_error_days: Optional[str] = None
    uncertainty: Optional[dict] = None


class NSDate(BaseModel):
    """Nepal Sambat date."""
    year: int
    formatted: str


class TithiInfo(BaseModel):
    """Tithi information."""
    tithi: int
    paksha: str
    tithi_name: str
    moon_phase: str
    method: str = "udaya"
    confidence: str = "exact"
    reference_time: str = "sunrise"
    sunrise_used: Optional[str] = None
    uncertainty: Optional[dict] = None


class ConversionResult(BaseModel):
    """Full calendar conversion result."""
    gregorian: str
    bikram_sambat: BSDate
    nepal_sambat: Optional[NSDate]
    tithi: TithiInfo
    support_tier: str
    engine_path: str
    fallback_used: bool = False
    calibration_status: str
    engine_version: str = "v3"
    provenance: Optional[dict] = None
    policy: Optional[dict] = None


class BSConversionRequest(BaseModel):
    """Request for BS to Gregorian conversion."""
    year: int
    month: int
    day: int


class BSCompareResult(BaseModel):
    """BS conversion comparison result."""
    year: int
    month: int
    day: int
    month_name: str
    confidence: str
    source_range: Optional[str] = None
    estimated_error_days: Optional[str] = None


def _parse_iso_date(date_str: str) -> date:
    return service_parse_iso_date(date_str)


def _build_conversion_payload(gregorian_date: date) -> dict:
    return build_conversion_payload(gregorian_date)


@router.get("/convert", response_model=ConversionResult)
async def convert_date(
    date_str: str = Query(
        ...,
        alias="date",
        description="Gregorian date in YYYY-MM-DD format",
        examples={"default": {"summary": "Sample date", "value": "2026-02-15"}}
    )
):
    """
    Convert a Gregorian date to Bikram Sambat, Nepal Sambat, and get tithi.
    
    Returns complete calendar information for the given date.
    """
    gregorian_date = _parse_iso_date(date_str)
    return _build_conversion_payload(gregorian_date)


@router.get("/convert/compare")
async def compare_convert(
    date_str: str = Query(
        ...,
        alias="date",
        description="Gregorian date in YYYY-MM-DD format",
        examples={"default": {"summary": "Sample date", "value": "2026-02-15"}}
    )
):
    """
    Compare official vs estimated BS conversion for a Gregorian date.
    
    Returns both conversions when available.
    """
    gregorian_date = _parse_iso_date(date_str)
    return build_compare_conversion_payload(gregorian_date)


@router.get("/dual-month")
async def get_dual_month(
    year: int = Query(..., ge=1600, le=2600, description="Gregorian year"),
    month: int = Query(..., ge=1, le=12, description="Gregorian month 1-12"),
):
    """
    Return a dual-calendar month map (Gregorian + Bikram Sambat) for UI calendar views.

    Supports a dynamic ±200 year browsing window around the current Gregorian year.
    """
    return build_dual_month_payload(year, month)


@router.post("/bs-to-gregorian")
async def bs_to_gregorian_convert(request: BSConversionRequest):
    """
    Convert a Bikram Sambat date to Gregorian.
    """
    try:
        return build_bs_to_gregorian_payload(request.year, request.month, request.day)
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/today")
async def get_today(
    risk_mode: str = Query("standard", description="standard|strict"),
):
    """
    Get calendar information for today.
    Uses udaya tithi (official sunrise-based) for accuracy.
    """
    return build_today_payload(risk_mode=risk_mode)


@router.get("/today/proof-capsule")
async def get_today_proof_capsule(
    risk_mode: str = Query("strict", description="standard|strict"),
):
    payload = build_today_payload(risk_mode=risk_mode)
    return build_calendar_proof_capsule(
        surface="today",
        payload=payload,
        request={"risk_mode": risk_mode},
    )


@router.get("/tithi")
async def get_tithi_endpoint(
    date_str: str = Query(
        ...,
        alias="date",
        description="Gregorian date in YYYY-MM-DD format",
        examples={"default": {"summary": "Sample date", "value": "2026-02-15"}},
    ),
    latitude: float = Query(27.7172, ge=-90.0, le=90.0, description="Latitude"),
    longitude: float = Query(85.3240, ge=-180.0, le=180.0, description="Longitude"),
    risk_mode: str = Query("standard", description="standard|strict"),
):
    """
    Get tithi details for a date/location with method metadata.
    """
    target_date = _parse_iso_date(date_str)
    return build_tithi_detail_payload(
        target_date,
        latitude=latitude,
        longitude=longitude,
        risk_mode=risk_mode,
    )


@router.get("/tithi/proof-capsule")
async def get_tithi_proof_capsule(
    date_str: str = Query(
        ...,
        alias="date",
        description="Gregorian date in YYYY-MM-DD format",
    ),
    latitude: float = Query(27.7172, ge=-90.0, le=90.0, description="Latitude"),
    longitude: float = Query(85.3240, ge=-180.0, le=180.0, description="Longitude"),
    risk_mode: str = Query("strict", description="standard|strict"),
):
    target_date = _parse_iso_date(date_str)
    payload = build_tithi_detail_payload(
        target_date,
        latitude=latitude,
        longitude=longitude,
        risk_mode=risk_mode,
    )
    return build_calendar_proof_capsule(
        surface="tithi",
        payload=payload,
        request={
            "date": target_date.isoformat(),
            "latitude": latitude,
            "longitude": longitude,
            "risk_mode": risk_mode,
        },
    )


# =============================================================================
# EPHEMERIS-BASED PANCHANGA (Full 5-element)
# =============================================================================

@router.get("/panchanga")
async def get_panchanga_endpoint(
    date_str: Optional[str] = Query(
        None,
        alias="date",
        description="Gregorian date in YYYY-MM-DD format",
        examples={"default": {"summary": "Sample date", "value": "2026-02-15"}}
    ),
    risk_mode: str = Query("standard", description="standard|strict"),
):
    """
    Get complete panchanga (5-element Hindu calendar) for a date.
    
    Uses Swiss Ephemeris for accurate astronomical calculations.
    Includes: Tithi, Nakshatra, Yoga, Karana, Vaara (weekday).
    """
    target_date = _parse_iso_date(date_str) if date_str else datetime.now().date()
    return build_panchanga_payload(target_date, risk_mode=risk_mode)


@router.get("/panchanga/proof-capsule")
async def get_panchanga_proof_capsule(
    date_str: str = Query(
        ...,
        alias="date",
        description="Gregorian date in YYYY-MM-DD format",
    ),
    risk_mode: str = Query("strict", description="standard|strict"),
):
    target_date = _parse_iso_date(date_str)
    payload = build_panchanga_payload(target_date, risk_mode=risk_mode)
    return build_calendar_proof_capsule(
        surface="panchanga",
        payload=payload,
        request={"date": target_date.isoformat(), "risk_mode": risk_mode},
    )


@router.get("/panchanga/range")
async def get_panchanga_range_endpoint(
    start_date: str = Query(..., alias="start", description="Start date YYYY-MM-DD"),
    days: int = Query(7, description="Number of days", ge=1, le=31)
):
    """
    Get panchanga for a range of dates.
    """
    start = _parse_iso_date(start_date)
    return build_panchanga_range_payload(start, days)


# =============================================================================
# FESTIVAL CALCULATION ENDPOINTS
# =============================================================================

@router.get("/festivals/calculate/{festival_id}")
async def calculate_festival_endpoint(
    festival_id: str,
    year: int = Query(..., description="Gregorian year", ge=2000, le=2100)
):
    """
    Calculate the dates for a specific festival in a given year.
    
    Uses V2 calculator with correct lunar month model and Adhik Maas handling.
    """
    from fastapi import HTTPException

    from app.calendar.calculator_v2 import calculate_festival_v2, get_festival_info_v2
    
    # Try V2 calculator first (lunar month model)
    result = calculate_festival_v2(festival_id, year)
    
    if result is None:
        # Check if festival exists but couldn't be calculated
        info = get_festival_info_v2(festival_id)
        if info is None:
            raise HTTPException(status_code=404, detail=f"Unknown festival: {festival_id}")
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Could not calculate {festival_id} for {year}"
            )
    
    return {
        "festival_id": festival_id,
        "year": year,
        "start": result.start_date.isoformat(),
        "end": result.end_date.isoformat(),
        "duration_days": result.duration_days,
        "method": result.method,
        "lunar_month": result.lunar_month,
        "is_adhik_year": result.is_adhik_year,
        "engine_version": "v3",
        "provenance": build_provenance(festival_id=festival_id, year=year),
        "policy": get_policy_metadata(),
    }


@router.get("/festivals/upcoming")
async def get_upcoming_festivals_endpoint(
    days: int = Query(30, description="Days to look ahead", ge=1, le=365)
):
    """
    Get all festivals occurring within the next N days.
    Uses V2 calculator with correct lunar month model.
    """
    return build_upcoming_festivals_payload(days, today=date.today())


@router.get("/sankranti/{year}")
async def get_sankrantis_endpoint(year: int):
    """
    Get all 12 sankrantis (solar transits) for a Gregorian year.
    """
    from app.calendar.sankranti import get_sankrantis_in_year
    
    sankrantis = get_sankrantis_in_year(year)
    
    return {
        "year": year,
        "sankrantis": [
            {
                "rashi": s["rashi_name"],
                "bs_month": s["bs_month"],
                "date": s["date"].isoformat(),
            }
            for s in sankrantis
        ],
        "engine_version": "v3",
        "provenance": build_provenance(),
        "policy": get_policy_metadata(),
    }
