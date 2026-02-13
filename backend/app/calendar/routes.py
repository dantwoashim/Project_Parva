"""
Calendar API Routes
===================

Endpoints for calendar conversion and tithi information.
"""

from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.calendar.bikram_sambat import (
    gregorian_to_bs,
    gregorian_to_bs_official,
    gregorian_to_bs_estimated,
    bs_to_gregorian,
    get_bs_month_name,
    get_bs_confidence,
    get_bs_year_confidence,
    get_bs_source_range,
    get_bs_estimated_error_days,
)
from app.calendar.constants import BS_MIN_YEAR, BS_MAX_YEAR
from app.calendar.nepal_sambat import get_current_ns_year, format_ns_date
from app.calendar.tithi import (
    calculate_tithi,
    get_tithi_name,
    get_moon_phase_name,
    get_udaya_tithi,  # Official (sunrise-based) tithi
)
from app.calendar.ephemeris.swiss_eph import calculate_sunrise
from app.calendar.ephemeris.time_utils import to_nepal_time
from app.provenance import get_latest_snapshot_id, get_provenance_payload
from app.cache import load_precomputed_festival_year, load_precomputed_panchanga
from app.policy import get_policy_metadata
from app.uncertainty import (
    build_bs_uncertainty,
    build_panchanga_uncertainty,
    build_tithi_uncertainty,
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
    engine_version: str = "v2"
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


def _build_provenance(festival_id: Optional[str] = None, year: Optional[int] = None) -> dict:
    snapshot_id = get_latest_snapshot_id()
    verify_url = "/v2/api/provenance/root"
    if festival_id and year and snapshot_id:
        verify_url = (
            f"/v2/api/provenance/proof?festival={festival_id}&year={year}&snapshot={snapshot_id}"
        )
    return get_provenance_payload(verify_url=verify_url, create_if_missing=True)


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
    # Parse date
    try:
        parts = date_str.split("-")
        gregorian_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Convert to BS
    bs_year, bs_month, bs_day = gregorian_to_bs(gregorian_date)
    bs_date = BSDate(
        year=bs_year,
        month=bs_month,
        day=bs_day,
        month_name=get_bs_month_name(bs_month),
        confidence=get_bs_confidence(gregorian_date),
        source_range=get_bs_source_range(gregorian_date),
        estimated_error_days=get_bs_estimated_error_days(gregorian_date),
        uncertainty=build_bs_uncertainty(
            get_bs_confidence(gregorian_date),
            get_bs_estimated_error_days(gregorian_date),
        ),
    )
    
    # Convert to NS
    try:
        ns_year = get_current_ns_year(gregorian_date)
        ns_date = NSDate(
            year=ns_year,
            formatted=format_ns_date(gregorian_date)
        )
    except Exception:
        ns_date = None
    
    # Calculate tithi using UDAYA method (official tithi at sunrise)
    # This avoids the "off by one day" issue near tithi boundaries
    try:
        udaya = get_udaya_tithi(gregorian_date)
        sunrise_utc = calculate_sunrise(gregorian_date)
        tithi_info = TithiInfo(
            tithi=udaya["tithi"],  # display number 1-15
            paksha=udaya["paksha"],
            tithi_name=udaya["name"],
            moon_phase=get_moon_phase_name(to_nepal_time(sunrise_utc)),
            method="ephemeris_udaya",
            confidence="exact",
            reference_time="sunrise",
            sunrise_used=to_nepal_time(sunrise_utc).isoformat(),
            uncertainty=build_tithi_uncertainty(
                method="ephemeris_udaya",
                confidence="exact",
                progress=udaya.get("progress"),
            ),
        )
    except Exception:
        # Fallback to instantaneous if sunrise calc fails
        tithi_data = calculate_tithi(gregorian_date)
        tithi_info = TithiInfo(
            tithi=tithi_data["display_number"],
            paksha=tithi_data["paksha"],
            tithi_name=tithi_data["name"],
            moon_phase=get_moon_phase_name(gregorian_date),
            method="instantaneous",
            confidence="computed",
            reference_time="instantaneous",
            uncertainty=build_tithi_uncertainty(
                method="instantaneous",
                confidence="computed",
                progress=tithi_data.get("progress"),
            ),
        )
    
    result = {
        "gregorian": gregorian_date.isoformat(),
        "bikram_sambat": {
            "year": bs_date.year,
            "month": bs_date.month,
            "day": bs_date.day,
            "month_name": bs_date.month_name,
            "confidence": bs_date.confidence,
            "source_range": bs_date.source_range,
            "estimated_error_days": bs_date.estimated_error_days,
            "uncertainty": bs_date.uncertainty,
        },
        "nepal_sambat": ns_date.model_dump() if ns_date else None,
        "tithi": {
            "tithi": tithi_info.tithi,
            "paksha": tithi_info.paksha,
            "tithi_name": tithi_info.tithi_name,
            "moon_phase": tithi_info.moon_phase,
            "method": tithi_info.method,
            "confidence": tithi_info.confidence,
            "reference_time": tithi_info.reference_time,
            "sunrise_used": tithi_info.sunrise_used,
            "uncertainty": tithi_info.uncertainty,
        },
        "engine_version": "v2",
        "provenance": _build_provenance(),
        "policy": get_policy_metadata(),
    }
    return result


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
    # Parse date
    try:
        parts = date_str.split("-")
        gregorian_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    official = None
    try:
        o_year, o_month, o_day = gregorian_to_bs_official(gregorian_date)
        official = {
            "year": o_year,
            "month": o_month,
            "day": o_day,
            "month_name": get_bs_month_name(o_month),
            "confidence": "official",
            "source_range": f"{BS_MIN_YEAR}-{BS_MAX_YEAR}",
            "estimated_error_days": None,
            "uncertainty": build_bs_uncertainty("official", None),
        }
    except Exception:
        official = None
    
    try:
        e_year, e_month, e_day = gregorian_to_bs_estimated(gregorian_date)
        estimated = {
            "year": e_year,
            "month": e_month,
            "day": e_day,
            "month_name": get_bs_month_name(e_month),
            "confidence": "estimated",
            "source_range": None,
            "estimated_error_days": "0-1",
            "uncertainty": build_bs_uncertainty("estimated", "0-1"),
        }
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))
    
    match = None
    if official:
        match = (
            official["year"] == estimated["year"]
            and official["month"] == estimated["month"]
            and official["day"] == estimated["day"]
        )
    
    return {
        "gregorian": gregorian_date.isoformat(),
        "official": official,
        "estimated": estimated,
        "match": match,
        "engine_version": "v2",
        "provenance": _build_provenance(),
        "policy": get_policy_metadata(),
    }


@router.post("/bs-to-gregorian")
async def bs_to_gregorian_convert(request: BSConversionRequest):
    """
    Convert a Bikram Sambat date to Gregorian.
    """
    try:
        gregorian_date = bs_to_gregorian(request.year, request.month, request.day)
        return {
            "bs": {
                "year": request.year,
                "month": request.month,
                "day": request.day,
                "month_name": get_bs_month_name(request.month),
                "confidence": get_bs_year_confidence(request.year),
                "source_range": f"{BS_MIN_YEAR}-{BS_MAX_YEAR}" if get_bs_year_confidence(request.year) == "official" else None,
                "estimated_error_days": "0-1" if get_bs_year_confidence(request.year) == "estimated" else None,
                "uncertainty": build_bs_uncertainty(
                    get_bs_year_confidence(request.year),
                    "0-1" if get_bs_year_confidence(request.year) == "estimated" else None,
                ),
            },
            "gregorian": gregorian_date.isoformat(),
            "engine_version": "v2",
            "provenance": _build_provenance(),
            "policy": get_policy_metadata(),
        }
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/today")
async def get_today():
    """
    Get calendar information for today.
    Uses udaya tithi (official sunrise-based) for accuracy.
    """
    today = date.today()
    
    # Convert to BS
    bs_year, bs_month, bs_day = gregorian_to_bs(today)
    
    # Calculate tithi using UDAYA method (official sunrise-based)
    try:
        udaya = get_udaya_tithi(today)
        sunrise_utc = calculate_sunrise(today)
        tithi_response = {
            "tithi": udaya["tithi"],  # display number 1-15
            "paksha": udaya["paksha"],
            "tithi_name": udaya["name"],
            "moon_phase": get_moon_phase_name(to_nepal_time(sunrise_utc)),
            "method": "ephemeris_udaya",
            "confidence": "exact",
            "reference_time": "sunrise",
            "sunrise_used": to_nepal_time(sunrise_utc).isoformat(),
            "uncertainty": build_tithi_uncertainty(
                method="ephemeris_udaya",
                confidence="exact",
                progress=udaya.get("progress"),
            ),
        }
    except Exception:
        # Fallback to instantaneous
        tithi_data = calculate_tithi(today)
        tithi_response = {
            "tithi": tithi_data["display_number"],
            "paksha": tithi_data["paksha"],
            "tithi_name": tithi_data["name"],
            "moon_phase": get_moon_phase_name(today),
            "method": "instantaneous",
            "confidence": "computed",
            "reference_time": "instantaneous",
            "sunrise_used": None,
            "uncertainty": build_tithi_uncertainty(
                method="instantaneous",
                confidence="computed",
                progress=tithi_data.get("progress"),
            ),
        }
    
    return {
        "gregorian": today.isoformat(),
        "bikram_sambat": {
            "year": bs_year,
            "month": bs_month,
            "day": bs_day,
            "month_name": get_bs_month_name(bs_month),
            "formatted": f"{bs_year} {get_bs_month_name(bs_month)} {bs_day}",
            "confidence": get_bs_confidence(today),
            "source_range": get_bs_source_range(today),
            "estimated_error_days": get_bs_estimated_error_days(today),
            "uncertainty": build_bs_uncertainty(
                get_bs_confidence(today),
                get_bs_estimated_error_days(today),
            ),
        },
        "tithi": tithi_response,
        "engine_version": "v2",
        "provenance": _build_provenance(),
        "policy": get_policy_metadata(),
    }


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
):
    """
    Get tithi details for a date/location with method metadata.
    """
    from app.calendar.tithi.tithi_udaya import detect_vriddhi, detect_ksheepana

    try:
        parts = date_str.split("-")
        target_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    try:
        udaya = get_udaya_tithi(target_date, latitude=latitude, longitude=longitude)
        sunrise_npt = udaya["sunrise_local"]
        return {
            "date": target_date.isoformat(),
            "location": {"latitude": latitude, "longitude": longitude},
            "tithi": {
                "number": udaya["tithi_absolute"],
                "display_number": udaya["tithi"],
                "paksha": udaya["paksha"],
                "name": udaya["name"],
                "progress": udaya["progress"],
                "moon_phase": get_moon_phase_name(sunrise_npt),
                "method": "ephemeris_udaya",
                "confidence": "exact",
                "reference_time": "sunrise",
                "sunrise_used": sunrise_npt.isoformat(),
                "vriddhi": detect_vriddhi(target_date, latitude=latitude, longitude=longitude),
                "ksheepana": detect_ksheepana(target_date, latitude=latitude, longitude=longitude),
                "uncertainty": build_tithi_uncertainty(
                    method="ephemeris_udaya",
                    confidence="exact",
                    progress=udaya.get("progress"),
                ),
            },
            "engine_version": "v2",
            "provenance": _build_provenance(),
            "policy": get_policy_metadata(),
        }
    except Exception:
        # Explicit fallback path for resilience.
        tithi_data = calculate_tithi(target_date)
        return {
            "date": target_date.isoformat(),
            "location": {"latitude": latitude, "longitude": longitude},
            "tithi": {
                "number": tithi_data["number"],
                "display_number": tithi_data["display_number"],
                "paksha": tithi_data["paksha"],
                "name": tithi_data["name"],
                "progress": tithi_data["progress"],
                "moon_phase": get_moon_phase_name(target_date),
                "method": "instantaneous",
                "confidence": "computed",
                "reference_time": "instantaneous",
                "sunrise_used": None,
                "vriddhi": False,
                "ksheepana": False,
                "uncertainty": build_tithi_uncertainty(
                    method="instantaneous",
                    confidence="computed",
                    progress=tithi_data.get("progress"),
                ),
            },
            "engine_version": "v2",
            "provenance": _build_provenance(),
            "policy": get_policy_metadata(),
        }


# =============================================================================
# EPHEMERIS-BASED PANCHANGA (Full 5-element)
# =============================================================================

@router.get("/panchanga")
async def get_panchanga_endpoint(
    date_str: str = Query(
        ...,
        alias="date",
        description="Gregorian date in YYYY-MM-DD format",
        examples={"default": {"summary": "Sample date", "value": "2026-02-15"}}
    )
):
    """
    Get complete panchanga (5-element Hindu calendar) for a date.
    
    Uses Swiss Ephemeris for accurate astronomical calculations.
    Includes: Tithi, Nakshatra, Yoga, Karana, Vaara (weekday).
    """
    from app.calendar.panchanga import get_panchanga
    
    # Parse date
    try:
        parts = date_str.split("-")
        target_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    cached_payload = load_precomputed_panchanga(target_date)
    if cached_payload:
        # Keep precomputed payload authoritative for heavy fields and attach live metadata.
        response = dict(cached_payload)
        response["date"] = target_date.isoformat()
        response["engine_version"] = "v2"
        response["provenance"] = _build_provenance()
        response["policy"] = get_policy_metadata()
        response["service_status"] = "degraded_cached" if response.get("cache", {}).get("stale") else "healthy"
        response["cache"] = {
            "hit": True,
            "source": "precomputed",
        }
        return response

    # Get full panchanga from ephemeris
    try:
        panchanga = get_panchanga(target_date)
    except Exception:
        # Degraded mode: ephemeris compute unavailable and no precomputed artifact found.
        from fastapi import HTTPException

        raise HTTPException(
            status_code=503,
            detail=(
                "Panchanga engine unavailable and no precomputed artifact found for "
                f"{target_date.isoformat()}. Run precompute pipeline or retry."
            ),
        )
    
    # Convert to BS
    bs_year, bs_month, bs_day = gregorian_to_bs(target_date)
    
    return {
        "date": target_date.isoformat(),
        "bikram_sambat": {
            "year": bs_year,
            "month": bs_month,
            "day": bs_day,
            "month_name": get_bs_month_name(bs_month),
            "confidence": get_bs_confidence(target_date),
            "source_range": get_bs_source_range(target_date),
            "estimated_error_days": get_bs_estimated_error_days(target_date),
            "uncertainty": build_bs_uncertainty(
                get_bs_confidence(target_date),
                get_bs_estimated_error_days(target_date),
            ),
        },
        "panchanga": {
            "confidence": "astronomical",
            "uncertainty": build_panchanga_uncertainty(),
            "tithi": {
                "number": panchanga["tithi"]["number"],
                "name": panchanga["tithi"]["name"],
                "paksha": panchanga["tithi"]["paksha"],
                "progress": panchanga["tithi"]["progress"],
                "method": "ephemeris_udaya",
                "confidence": "exact",
                "reference_time": "sunrise",
                "sunrise_used": panchanga["sunrise"]["local"],
            },
            "nakshatra": {
                "number": panchanga["nakshatra"]["number"],
                "name": panchanga["nakshatra"]["name"],
                "pada": panchanga["nakshatra"].get("pada", 1),
            },
            "yoga": {
                "number": panchanga["yoga"]["number"],
                "name": panchanga["yoga"]["name"],
            },
            "karana": {
                "number": panchanga["karana"]["number"],
                "name": panchanga["karana"]["name"],
            },
            "vaara": {
                "name_sanskrit": panchanga["vaara"]["name_sanskrit"],
                "name_english": panchanga["vaara"]["name_english"],
            },
        },
        "ephemeris": {
            "mode": panchanga.get("mode", "swiss_moshier"),
            "accuracy": panchanga.get("accuracy", "arcsecond"),
            "library": panchanga.get("library", "pyswisseph"),
        },
        "cache": {
            "hit": False,
            "source": "computed",
        },
        "service_status": "healthy",
        "engine_version": "v2",
        "provenance": _build_provenance(),
        "policy": get_policy_metadata(),
    }


@router.get("/panchanga/range")
async def get_panchanga_range_endpoint(
    start_date: str = Query(..., alias="start", description="Start date YYYY-MM-DD"),
    days: int = Query(7, description="Number of days", ge=1, le=31)
):
    """
    Get panchanga for a range of dates.
    """
    from app.calendar.panchanga import get_panchanga
    
    try:
        parts = start_date.split("-")
        start = date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    results = []
    cache_hits = 0
    cache_misses = 0
    for offset in range(days):
        d = start + timedelta(days=offset)
        cached = load_precomputed_panchanga(d)
        if cached:
            p = {
                "date": d.isoformat(),
                "tithi": cached["panchanga"]["tithi"]["name"],
                "nakshatra": cached["panchanga"]["nakshatra"]["name"],
                "yoga": cached["panchanga"]["yoga"]["name"],
                "vaara": cached["panchanga"]["vaara"]["name_english"],
            }
            cache_hits += 1
            results.append(p)
            continue

        # Fallback to live compute.
        p = get_panchanga(d)
        results.append({
            "date": p["date"].isoformat() if hasattr(p["date"], "isoformat") else str(p["date"]),
            "tithi": p["tithi"]["name"],
            "nakshatra": p["nakshatra"]["name"],
            "yoga": p["yoga"]["name"],
            "vaara": p["vaara"]["name_english"],
        })
        cache_misses += 1
    
    return {
        "start": start.isoformat(),
        "days": days,
        "panchangas": results,
        "cache": {
            "hits": cache_hits,
            "misses": cache_misses,
            "hit_ratio": round(cache_hits / days, 4) if days else 0.0,
        },
        "engine_version": "v2",
        "provenance": _build_provenance(),
        "policy": get_policy_metadata(),
    }


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
    from app.calendar.calculator_v2 import calculate_festival_v2, get_festival_info_v2
    from fastapi import HTTPException
    
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
        "engine_version": "v2",
        "provenance": _build_provenance(festival_id=festival_id, year=year),
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
    from app.calendar.calculator_v2 import calculate_festival_v2, list_festivals_v2
    
    today = date.today()
    end_date = today + timedelta(days=days)
    
    upcoming = []
    cache_years_loaded: list[int] = []

    # Fast path: use precomputed yearly artifacts if present.
    for year in [today.year, today.year + 1]:
        payload = load_precomputed_festival_year(year)
        if not payload or not isinstance(payload.get("festivals"), list):
            continue
        cache_years_loaded.append(year)
        for row in payload["festivals"]:
            try:
                start_dt = date.fromisoformat(str(row["start"]))
                end_dt = date.fromisoformat(str(row["end"]))
            except Exception:
                continue
            if start_dt < today or start_dt > end_date:
                continue
            upcoming.append({
                "festival_id": row["festival_id"],
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat(),
                "days_until": (start_dt - today).days,
            })

    if cache_years_loaded:
        upcoming.sort(key=lambda x: x["start"])
        return {
            "from_date": today.isoformat(),
            "days": days,
            "festivals": upcoming,
            "cache": {
                "hit": True,
                "years_loaded": sorted(set(cache_years_loaded)),
                "source": "precomputed",
            },
            "engine_version": "v2",
            "provenance": _build_provenance(),
            "policy": get_policy_metadata(),
        }

    for fid in list_festivals_v2():
        result = calculate_festival_v2(fid, today.year)
        if result and result.start_date >= today and result.start_date <= end_date:
            upcoming.append({
                "festival_id": fid,
                "start": result.start_date.isoformat(),
                "end": result.end_date.isoformat(),
                "days_until": (result.start_date - today).days,
            })
        # Also check next year for early-year festivals
        elif result and result.start_date < today:
            result_next = calculate_festival_v2(fid, today.year + 1)
            if result_next and result_next.start_date <= end_date:
                upcoming.append({
                    "festival_id": fid,
                    "start": result_next.start_date.isoformat(),
                    "end": result_next.end_date.isoformat(),
                    "days_until": (result_next.start_date - today).days,
                })
    
    # Sort by start date
    upcoming.sort(key=lambda x: x["start"])
    
    return {
        "from_date": today.isoformat(),
        "days": days,
        "festivals": upcoming,
        "cache": {
            "hit": False,
            "years_loaded": [],
            "source": "computed",
        },
        "engine_version": "v2",
        "provenance": _build_provenance(),
        "policy": get_policy_metadata(),
    }


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
        "engine_version": "v2",
        "provenance": _build_provenance(),
        "policy": get_policy_metadata(),
    }
