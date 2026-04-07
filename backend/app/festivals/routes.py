"""
Festival API Routes
===================

FastAPI routes for festival discovery endpoints.
"""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from ..calendar.overrides import get_festival_override_info
from ..rules import get_rule_service
from ..rules.catalog_v4 import (
    get_rule_v4,
)
from ..rules.variants import calculate_with_variants, filter_variants_by_profile, list_profiles
from .detail_service import build_festival_explain_payload
from .models import (
    FestivalCalendarResponse,
    FestivalDates,
    FestivalDetailResponse,
    FestivalDisputeAtlasResponse,
    FestivalExplainResponse,
    FestivalListResponse,
    FestivalProofCapsuleResponse,
    FestivalSummary,
    UpcomingFestivalsResponse,
)
from .query_service import (
    apply_profile_variant_to_dates,
    validate_authority_mode,
    validate_profile,
)
from .repository import get_repository
from .risk_service import truth_ladder
from .trust import build_provenance
from .use_cases import (
    calendar_month_payload,
    coverage_payload,
    coverage_scoreboard_payload,
    dispute_atlas_payload,
    festival_detail_payload,
    festivals_on_date_payload,
    list_festivals_payload,
    upcoming_festivals_payload,
)

router = APIRouter(prefix="/api/festivals", tags=["festivals"])
rule_service = get_rule_service()

@router.get("", response_model=FestivalListResponse)
async def list_festivals(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by name or description"),
    region: Optional[str] = Query(None, description="Filter by region focus"),
    tradition: Optional[str] = Query(None, description="Filter by tradition/category"),
    source: Optional[str] = Query(
        None, description="Filter by rule source (e.g., festival_rules_v3)"
    ),
    quality_band: str = Query("all", description="computed|provisional|inventory|all"),
    algorithmic_only: bool = Query(True, description="Only include algorithmic rules"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """
    List all festivals with optional filtering.

    Categories: national, newari, buddhist, regional
    """
    return list_festivals_payload(
        category=category,
        search=search,
        region=region,
        tradition=tradition,
        source=source,
        quality_band=quality_band,
        algorithmic_only=algorithmic_only,
        page=page,
        page_size=page_size,
    )


@router.get("/coverage")
async def get_festival_coverage(
    target_rules: int = Query(300, ge=1, le=5000, description="Target count for roadmap coverage"),
):
    """
    Return v4 rule-catalog coverage summary.

    Used to track progress from current rule count toward the long-term 300+ goal.
    """
    return coverage_payload(target_rules=target_rules)


@router.get("/coverage/scoreboard")
async def get_festival_coverage_scoreboard(
    target_rules: int = Query(300, ge=1, le=5000, description="Target computed-rule count"),
):
    """Return truth-first computed/provisional/inventory coverage scoreboard."""
    return coverage_scoreboard_payload(target_rules=target_rules)


@router.get("/disputes", response_model=FestivalDisputeAtlasResponse)
async def get_dispute_atlas(
    year: int = Query(..., ge=2000, le=2200, description="Gregorian year"),
    limit: int = Query(18, ge=1, le=100, description="Maximum number of dispute/risk rows"),
):
    """Return authority conflicts and risk-ranked festival-year rows for truth/dispute surfaces."""
    return dispute_atlas_payload(year=year, limit=limit)


@router.get("/upcoming", response_model=UpcomingFestivalsResponse)
async def get_upcoming(
    days: int = Query(30, ge=1, le=365, description="Number of days to look ahead"),
    from_date: Optional[date] = Query(None, description="Start date (defaults to today)"),
    quality_band: str = Query("computed", description="computed|provisional|inventory|all"),
    profile: Optional[str] = Query(None, description="Variant profile id"),
):
    """
    Get festivals occurring in the next N days.

    Returns festivals sorted by start date.
    """
    return upcoming_festivals_payload(
        days=days,
        from_date=from_date,
        quality_band=quality_band,
        profile=profile,
    )


@router.get("/on-date/{target_date}", response_model=List[FestivalSummary])
async def festivals_on_date(
    target_date: date,
    profile: Optional[str] = Query(None, description="Variant profile id"),
):
    """
    Get all festivals occurring on a specific date.

    Includes multi-day festivals that overlap with this date.
    """
    return festivals_on_date_payload(target_date=target_date, profile=profile)


@router.get("/calendar/{year}/{month}", response_model=FestivalCalendarResponse)
async def get_calendar_month(
    year: int,
    month: int,
    profile: Optional[str] = Query(None, description="Variant profile id"),
):
    """
    Get festivals for a calendar month view.

    Returns each day of the month with any festivals on that day.
    """
    return calendar_month_payload(year=year, month=month, profile=profile)


@router.get("/{festival_id}", response_model=FestivalDetailResponse)
async def get_festival(
    festival_id: str,
    year: Optional[int] = Query(None, description="Year for date calculation"),
    profile: Optional[str] = Query(None, description="Variant profile id"),
    authority_mode: str = Query(
        "public_default",
        description="public_default|authority_compare|all_candidates",
    ),
    risk_mode: str = Query("standard", description="standard|strict"),
):
    """
    Get detailed information about a specific festival.

    Includes full content (mythology, rituals) and calculated dates.
    """
    authority_mode = validate_authority_mode(authority_mode)
    return festival_detail_payload(
        festival_id=festival_id,
        year=year,
        profile=profile,
        authority_mode=authority_mode,
        risk_mode=risk_mode,
    )


@router.get("/{festival_id}/explain", response_model=FestivalExplainResponse)
async def explain_festival_date(
    festival_id: str,
    year: Optional[int] = Query(None, description="Gregorian year for explanation"),
    profile: Optional[str] = Query(None, description="Variant profile id"),
    authority_mode: str = Query(
        "public_default",
        description="public_default|authority_compare|all_candidates",
    ),
    risk_mode: str = Query("standard", description="standard|strict"),
):
    """
    Explain why a festival resolves to a specific date in the selected year.
    """
    repo = get_repository()
    authority_mode = validate_authority_mode(authority_mode)
    festival = repo.get_by_id(festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail=f"Festival '{festival_id}' not found")

    target_year = year or date.today().year
    date_result = rule_service.calculate(festival_id, target_year)
    if not date_result:
        raise HTTPException(
            status_code=404, detail=f"Could not calculate '{festival_id}' for {target_year}"
        )

    override_info = get_festival_override_info(
        festival_id,
        target_year,
        authority_mode=authority_mode,
    )
    payload = build_festival_explain_payload(
        festival=festival,
        festival_id=festival_id,
        target_year=target_year,
        date_result=date_result,
        authority_mode=authority_mode,
        profile=profile,
        override_info=override_info,
        risk_mode=risk_mode,
    )

    return FestivalExplainResponse(**payload.__dict__)


@router.get("/{festival_id}/proof-capsule", response_model=FestivalProofCapsuleResponse)
async def get_festival_proof_capsule(
    festival_id: str,
    year: int = Query(..., ge=2000, le=2200, description="Gregorian year"),
    authority_mode: str = Query("authority_compare", description="public_default|authority_compare|all_candidates"),
    risk_mode: str = Query("strict", description="standard|strict"),
):
    """Return a portable proof capsule for one festival-year resolution."""
    repo = get_repository()
    authority_mode = validate_authority_mode(authority_mode)
    festival = repo.get_by_id(festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail=f"Festival '{festival_id}' not found")

    date_result = rule_service.calculate(festival_id, year)
    if not date_result:
        raise HTTPException(status_code=404, detail=f"Could not calculate '{festival_id}' for {year}")

    override_info = get_festival_override_info(
        festival_id,
        year,
        authority_mode=authority_mode,
    )
    explain = build_festival_explain_payload(
        festival=festival,
        festival_id=festival_id,
        target_year=year,
        date_result=date_result,
        authority_mode=authority_mode,
        profile=None,
        override_info=override_info,
        risk_mode=risk_mode,
    )

    return FestivalProofCapsuleResponse(
        festival_id=festival_id,
        festival_name=festival.name,
        year=year,
        request={
            "festival_id": festival_id,
            "year": year,
            "authority_mode": authority_mode,
            "risk_mode": risk_mode,
        },
        selection={
            "start_date": explain.start_date,
            "end_date": explain.end_date,
            "method": explain.method,
            "selection_policy": explain.selection_policy,
            "support_tier": explain.support_tier,
            "engine_path": explain.engine_path,
            "fallback_used": explain.fallback_used,
            "calibration_status": explain.calibration_status,
            "abstained": explain.abstained,
        },
        source_lineage={
            "source_family": explain.source_family,
            "authority_conflict": explain.authority_conflict,
            "alternate_candidates": explain.alternate_candidates,
            "authority_suggested_profile_id": explain.authority_suggested_profile_id,
            "authority_suggested_start_date": explain.authority_suggested_start_date,
            "authority_suggested_reason": explain.authority_suggested_reason,
            "rule_summary": explain.rule_summary,
        },
        risk={
            "boundary_radar": explain.boundary_radar,
            "stability_score": explain.stability_score,
            "risk_mode": explain.risk_mode,
            "recommended_action": explain.recommended_action,
            "truth_ladder": truth_ladder(),
        },
        provenance=explain.provenance,
        calculation_trace_id=explain.calculation_trace_id,
    )


@router.get("/{festival_id}/dates", response_model=List[FestivalDates])
async def get_festival_dates(
    festival_id: str,
    years: int = Query(3, ge=1, le=10, description="Number of years to return"),
    start_year: Optional[int] = Query(None, description="Starting year"),
    profile: Optional[str] = Query(None, description="Variant profile id"),
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
    validate_profile(profile)
    results = []

    for year in range(start, start + years):
        dates, availability = repo.get_dates_with_availability(festival_id, year)
        if dates:
            dates, _profile_note = apply_profile_variant_to_dates(festival_id, year, dates, profile)
            dates.provenance = build_provenance(festival_id=festival_id, year=year)
            results.append(dates)

    if not results:
        raise HTTPException(
            status_code=404, detail=f"Could not calculate dates for '{festival_id}'"
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
        "provenance": build_provenance(festival_id=festival_id, year=year),
    }
