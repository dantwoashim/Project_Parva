"""
Festival API Routes
===================

FastAPI routes for festival discovery endpoints.
"""

from __future__ import annotations

from datetime import date
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query

from .repository import get_repository
from .models import (
    Festival,
    FestivalSummary,
    FestivalListResponse,
    FestivalDetailResponse,
    FestivalDates,
    UpcomingFestival,
    UpcomingFestivalsResponse,
    CalendarDayFestivals,
    FestivalCalendarResponse,
    FestivalExplainResponse,
    ProvenanceMeta,
)
from ..calendar import (
    gregorian_to_bs,
    calculate_tithi,
    get_bs_month_name,
)
from ..rules import get_rule_service
from ..rules.variants import calculate_with_variants, filter_variants_by_profile, list_profiles
from ..rules.catalog_v4 import get_rule_v4, get_rules_coverage
from ..provenance import get_latest_snapshot_id, get_provenance_payload
from ..explainability import create_reason_trace


router = APIRouter(prefix="/api/festivals", tags=["festivals"])
rule_service = get_rule_service()


def _build_provenance(
    festival_id: Optional[str] = None,
    year: Optional[int] = None,
) -> ProvenanceMeta:
    snapshot_id = get_latest_snapshot_id()
    verify_url = "/v2/api/provenance/root"
    if festival_id and year and snapshot_id:
        verify_url = (
            f"/v2/api/provenance/proof?festival={festival_id}&year={year}&snapshot={snapshot_id}"
        )
    return ProvenanceMeta(**get_provenance_payload(verify_url=verify_url, create_if_missing=True))


@router.get("", response_model=FestivalListResponse)
async def list_festivals(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by name or description"),
    region: Optional[str] = Query(None, description="Filter by region focus"),
    tradition: Optional[str] = Query(None, description="Filter by tradition/category"),
    source: Optional[str] = Query(None, description="Filter by rule source (e.g., festival_rules_v3)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """
    List all festivals with optional filtering.
    
    Categories: national, newari, buddhist, regional
    """
    repo = get_repository()
    
    festivals = repo.search(search) if search else repo.get_all()

    if category:
        festivals = [f for f in festivals if f.category == category]

    if region:
        region_l = region.lower()
        festivals = [
            f for f in festivals
            if any(region_l in r.lower() for r in (f.regional_focus or []))
        ]

    if tradition:
        tradition_l = tradition.lower()
        festivals = [
            f for f in festivals
            if tradition_l in f.category.lower()
            or tradition_l in (f.who_celebrates or "").lower()
        ]

    if source:
        source_l = source.lower()
        filtered = []
        for festival in festivals:
            rule = get_rule_v4(festival.id)
            if rule and source_l in rule.source.lower():
                filtered.append(festival)
        festivals = filtered
    
    # Sort by significance level (highest first)
    festivals.sort(key=lambda f: f.significance_level, reverse=True)
    
    # Paginate
    start = (page - 1) * page_size
    end = start + page_size
    paginated = festivals[start:end]
    
    # Convert to summaries
    summaries = [repo.to_summary(f) for f in paginated]
    
    return FestivalListResponse(
        festivals=summaries,
        total=len(festivals),
        page=page,
        page_size=page_size,
        provenance=_build_provenance(),
    )


@router.get("/coverage")
async def get_festival_coverage(
    target_rules: int = Query(300, ge=1, le=5000, description="Target count for roadmap coverage"),
):
    """
    Return v4 rule-catalog coverage summary.

    Used to track progress from current rule count toward the long-term 300+ goal.
    """
    repo = get_repository()
    coverage = get_rules_coverage(target=target_rules)
    content_count = len(repo.get_all())
    coverage["festival_content_count"] = content_count
    coverage["content_rule_gap"] = max(coverage["total_rules"] - content_count, 0)
    coverage["provenance"] = _build_provenance().model_dump()
    return coverage


@router.get("/upcoming", response_model=UpcomingFestivalsResponse)
async def get_upcoming(
    days: int = Query(30, ge=1, le=365, description="Number of days to look ahead"),
    from_date: Optional[date] = Query(None, description="Start date (defaults to today)"),
):
    """
    Get festivals occurring in the next N days.
    
    Returns festivals sorted by start date.
    """
    repo = get_repository()
    start = from_date or date.today()
    
    # Get upcoming from calendar engine
    upcoming = rule_service.upcoming(start, days=days)
    
    results = []
    for festival_id, dates in upcoming:
        festival = repo.get_by_id(festival_id)
        if festival:
            results.append(UpcomingFestival(
                id=festival.id,
                name=festival.name,
                name_nepali=festival.name_nepali,
                tagline=festival.tagline,
                category=festival.category,
                start_date=dates.start_date,
                end_date=dates.end_date,
                days_until=(dates.start_date - start).days,
                duration_days=dates.duration_days,
                primary_color=festival.primary_color,
            ))
    
    from datetime import timedelta
    
    return UpcomingFestivalsResponse(
        festivals=results,
        from_date=start,
        to_date=start + timedelta(days=days),
        total=len(results),
        provenance=_build_provenance(),
    )


@router.get("/on-date/{target_date}", response_model=List[FestivalSummary])
async def festivals_on_date(target_date: date):
    """
    Get all festivals occurring on a specific date.
    
    Includes multi-day festivals that overlap with this date.
    """
    repo = get_repository()
    
    festivals_data = rule_service.on_date(target_date)
    
    results = []
    for festival_id, dates in festivals_data:
        festival = repo.get_by_id(festival_id)
        if festival:
            summary = repo.to_summary(festival)
            summary.next_start = dates.start_date
            summary.next_end = dates.end_date
            results.append(summary)
    
    return results


@router.get("/calendar/{year}/{month}", response_model=FestivalCalendarResponse)
async def get_calendar_month(year: int, month: int):
    """
    Get festivals for a calendar month view.
    
    Returns each day of the month with any festivals on that day.
    """
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be 1-12")
    
    repo = get_repository()
    
    # Calculate first and last day of month
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    
    first_day = date(year, month, 1)
    last_day = next_month - __import__('datetime').timedelta(days=1)
    
    days = []
    current = first_day
    
    while current <= last_day:
        # Get festivals on this day
        festivals_data = rule_service.on_date(current)
        summaries = []
        for festival_id, dates in festivals_data:
            festival = repo.get_by_id(festival_id)
            if festival:
                summaries.append(repo.to_summary(festival))
        
        # Get tithi info
        try:
            tithi_info = calculate_tithi(current)
            tithi = tithi_info.get("display_number")
            paksha = tithi_info.get("paksha")
            bs_year, bs_month, bs_day = gregorian_to_bs(current)
            bs_str = f"{bs_day} {get_bs_month_name(bs_month)}"
        except (ValueError, TypeError):
            tithi = None
            paksha = None
            bs_str = None
        
        days.append(CalendarDayFestivals(
            date=current,
            bs_date=bs_str,
            festivals=summaries,
            tithi=tithi,
            paksha=paksha,
        ))
        
        current += __import__('datetime').timedelta(days=1)
    
    return FestivalCalendarResponse(
        days=days,
        month=month,
        year=year,
        provenance=_build_provenance(),
    )


@router.get("/{festival_id}", response_model=FestivalDetailResponse)
async def get_festival(
    festival_id: str,
    year: Optional[int] = Query(None, description="Year for date calculation"),
):
    """
    Get detailed information about a specific festival.
    
    Includes full content (mythology, rituals) and calculated dates.
    """
    repo = get_repository()
    
    festival = repo.get_by_id(festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail=f"Festival '{festival_id}' not found")
    
    # Get dates for specified year or current/next occurrence
    target_year = year or date.today().year
    dates = repo.get_dates(festival_id, target_year)
    
    if not dates and not year:
        # Try next year
        dates = repo.get_dates(festival_id, target_year + 1)
    
    if not dates:
        # No dates available - don't fake it, let frontend handle gracefully
        dates = None
    
    # Get nearby festivals (within 30 days of this festival)
    nearby = []
    if dates:
        from datetime import timedelta
        
        search_start = dates.start_date - timedelta(days=15)
        nearby_raw = rule_service.upcoming(search_start, days=45)
        
        for fid, fdates in nearby_raw[:5]:
            if fid != festival_id:
                f = repo.get_by_id(fid)
                if f:
                    nearby.append(repo.to_summary(f))
    
    return FestivalDetailResponse(
        festival=festival,
        dates=dates,
        nearby_festivals=nearby[:4] if nearby else None,
        provenance=_build_provenance(festival_id=festival_id, year=target_year),
    )


@router.get("/{festival_id}/explain", response_model=FestivalExplainResponse)
async def explain_festival_date(
    festival_id: str,
    year: Optional[int] = Query(None, description="Gregorian year for explanation"),
):
    """
    Explain why a festival resolves to a specific date in the selected year.
    """
    repo = get_repository()
    festival = repo.get_by_id(festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail=f"Festival '{festival_id}' not found")

    target_year = year or date.today().year
    date_result = rule_service.calculate(festival_id, target_year)
    if not date_result:
        raise HTTPException(status_code=404, detail=f"Could not calculate '{festival_id}' for {target_year}")

    rule = rule_service.info(festival_id)
    structured_steps = []
    if rule and getattr(rule, "type", None) == "lunar":
        rule_summary = (
            f"{rule.lunar_month} {str(rule.paksha).capitalize()} {rule.tithi}"
        )
        steps = [
            f"Load lunar rule for {festival.name}: {rule_summary}.",
            "Resolve lunar month boundaries (Amavasya to Amavasya).",
            "Compute udaya tithi (tithi at sunrise) for candidate dates.",
            f"Select date that matches required tithi/paksha in {target_year}.",
            f"Apply festival duration ({date_result.duration_days} day(s)).",
        ]
        explanation = (
            f"{festival.name} follows the lunar rule {rule_summary}. "
            f"For {target_year}, the matching udaya tithi resolves to "
            f"{date_result.start_date.isoformat()}."
        )
        structured_steps = [
            {
                "step_type": "load_rule",
                "input": {"festival_id": festival_id, "year": target_year},
                "output": {"rule_summary": rule_summary, "rule_type": "lunar"},
                "rule_id": festival_id,
                "source": "festival_rules_v3.json",
                "math_expression": None,
            },
            {
                "step_type": "lunar_month_window",
                "input": {"lunar_month": rule.lunar_month, "adhik_policy": rule.adhik_policy},
                "output": {"window_model": "amavasya_to_amavasya"},
                "rule_id": festival_id,
                "source": "lunar_calendar.py",
                "math_expression": "month = [new_moon_i, new_moon_(i+1))",
            },
            {
                "step_type": "tithi_resolution",
                "input": {"paksha": rule.paksha, "tithi": rule.tithi},
                "output": {"start_date": date_result.start_date.isoformat()},
                "rule_id": festival_id,
                "source": "tithi_udaya.py",
                "math_expression": "tithi = floor(((lambda_moon - lambda_sun) mod 360)/12)+1",
            },
        ]
    elif rule and getattr(rule, "type", None) == "solar":
        month = getattr(rule, "bs_month", None)
        solar_day = getattr(rule, "solar_day", None)
        rule_summary = (
            f"Solar rule (BS month={month}, day={solar_day})"
            if month and solar_day
            else "Solar sankranti rule"
        )
        steps = [
            f"Load solar rule for {festival.name}: {rule_summary}.",
            "Resolve corresponding sankranti/BS month boundary.",
            f"Map resulting BS date into Gregorian year {target_year}.",
            f"Apply festival duration ({date_result.duration_days} day(s)).",
        ]
        explanation = (
            f"{festival.name} follows a solar rule. "
            f"For {target_year}, the computed start date is {date_result.start_date.isoformat()}."
        )
        structured_steps = [
            {
                "step_type": "load_rule",
                "input": {"festival_id": festival_id, "year": target_year},
                "output": {"rule_summary": rule_summary, "rule_type": "solar"},
                "rule_id": festival_id,
                "source": "festival_rules_v3.json",
                "math_expression": None,
            },
            {
                "step_type": "solar_mapping",
                "input": {"bs_month": getattr(rule, "bs_month", None), "solar_day": getattr(rule, "solar_day", None)},
                "output": {"start_date": date_result.start_date.isoformat()},
                "rule_id": festival_id,
                "source": "sankranti.py",
                "math_expression": "find t where sun_longitude(t) = target_rashi_degree",
            },
        ]
    else:
        rule_summary = "Fallback legacy rule"
        steps = [
            "Festival is not yet in V3 lunar rule set.",
            "Use compatibility fallback calculation path.",
            f"Computed start date for {target_year}: {date_result.start_date.isoformat()}.",
        ]
        explanation = (
            f"{festival.name} used fallback rule handling for {target_year} "
            f"and resolved to {date_result.start_date.isoformat()}."
        )
        structured_steps = [
            {
                "step_type": "fallback",
                "input": {"festival_id": festival_id, "year": target_year},
                "output": {"start_date": date_result.start_date.isoformat(), "method": "fallback_v1"},
                "rule_id": festival_id,
                "source": "calculator.py",
                "math_expression": None,
            }
        ]

    trace = create_reason_trace(
        trace_type="festival_date_explain",
        subject={"festival_id": festival_id, "festival_name": festival.name},
        inputs={"year": target_year, "rule_summary": rule_summary},
        outputs={
            "start_date": date_result.start_date.isoformat(),
            "end_date": date_result.end_date.isoformat(),
            "method": date_result.method,
        },
        steps=structured_steps,
        provenance=_build_provenance(festival_id=festival_id, year=target_year).model_dump(),
    )
    trace_id = trace["trace_id"]
    confidence = "official" if date_result.method == "override" else "computed"

    return FestivalExplainResponse(
        festival_id=festival_id,
        festival_name=festival.name,
        year=target_year,
        start_date=date_result.start_date,
        end_date=date_result.end_date,
        method=date_result.method,
        confidence=confidence,
        rule_summary=rule_summary,
        explanation=explanation,
        steps=steps,
        calculation_trace_id=trace_id,
        provenance=_build_provenance(festival_id=festival_id, year=target_year),
    )


@router.get("/{festival_id}/dates", response_model=List[FestivalDates])
async def get_festival_dates(
    festival_id: str,
    years: int = Query(3, ge=1, le=10, description="Number of years to return"),
    start_year: Optional[int] = Query(None, description="Starting year"),
):
    """
    Get calculated dates for a festival across multiple years.
    
    Useful for planning and historical reference.
    """
    repo = get_repository()
    
    festival = repo.get_by_id(festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail=f"Festival '{festival_id}' not found")
    
    start = start_year or date.today().year
    results = []
    
    for year in range(start, start + years):
        dates = repo.get_dates(festival_id, year)
        if dates:
            dates.provenance = _build_provenance(festival_id=festival_id, year=year)
            results.append(dates)
    
    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"Could not calculate dates for '{festival_id}'"
        )
    
    return results


@router.get("/{festival_id}/variants")
async def get_festival_variants(
    festival_id: str,
    year: int = Query(..., ge=2000, le=2200, description="Gregorian year"),
    profile: Optional[str] = Query(None, description="Filter by profile id"),
):
    """
    Return documented regional/tradition variants for a festival date.
    """
    repo = get_repository()
    festival = repo.get_by_id(festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail=f"Festival '{festival_id}' not found")

    variants = calculate_with_variants(festival_id, year)
    variants = filter_variants_by_profile(variants, profile)
    if not variants:
        raise HTTPException(
            status_code=404,
            detail=f"Could not calculate variants for '{festival_id}' in {year}",
        )

    profiles = list_profiles()
    available_profile_ids = sorted({p.get("profile_id") for p in profiles if p.get("profile_id")})
    variant_profile_ids = sorted({v.get("profile_id") for v in variants if v.get("profile_id")})
    missing_profile_ids = [pid for pid in available_profile_ids if pid not in variant_profile_ids]
    profile_coverage_pct = (
        round((len(variant_profile_ids) / len(available_profile_ids)) * 100, 2)
        if available_profile_ids
        else 0.0
    )
    canonical_rule = get_rule_v4(festival_id)

    return {
        "festival_id": festival_id,
        "festival_name": festival.name,
        "year": year,
        "profile_filter": profile,
        "profiles": profiles,
        "coverage": {
            "available_profiles": len(available_profile_ids),
            "profiles_with_variant": len(variant_profile_ids),
            "profile_coverage_pct": profile_coverage_pct,
            "variant_count": len(variants),
            "missing_profiles": missing_profile_ids,
            "rule_family": canonical_rule.rule_family if canonical_rule else "unknown",
            "rule_source": canonical_rule.source if canonical_rule else "unknown",
        },
        "variants": variants,
        "provenance": _build_provenance(festival_id=festival_id, year=year),
    }
