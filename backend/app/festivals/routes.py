"""
Festival API Routes
===================

FastAPI routes for festival discovery endpoints.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from ..calendar import (
    calculate_tithi,
    get_bs_month_name,
    gregorian_to_bs,
)
from ..calendar.overrides import get_festival_override_info
from ..rules import get_rule_service
from ..rules.catalog_v4 import (
    get_rule_v4,
    get_rules_coverage,
    get_rules_scoreboard,
    rule_has_algorithm,
    rule_quality_band,
)
from ..rules.variants import calculate_with_variants, filter_variants_by_profile, list_profiles
from ..services.ritual_normalization import normalize_ritual_sequence
from ..core.request_context import derive_support_tier
from .detail_service import build_detail_completeness, build_festival_explain_payload
from .models import (
    CalendarDayFestivals,
    FestivalCalendarResponse,
    FestivalDateAvailability,
    FestivalDates,
    FestivalDetailResponse,
    FestivalDisputeAtlasResponse,
    FestivalDisputeRecord,
    FestivalExplainResponse,
    FestivalListResponse,
    FestivalProofCapsuleResponse,
    FestivalSummary,
    ProvenanceMeta,
    UpcomingFestival,
    UpcomingFestivalsResponse,
)
from .query_service import (
    apply_profile_variant_to_dates,
    calibration_status as route_calibration_status,
    collect_profile_occurrences,
    fallback_used as route_fallback_used,
    resolved_date_note,
    summary_for_occurrence,
    validate_authority_mode,
    validate_profile,
)
from .risk_service import build_risk_payload, truth_ladder
from .repository import get_repository
from .trust import build_provenance

router = APIRouter(prefix="/api/festivals", tags=["festivals"])
rule_service = get_rule_service()


QUALITY_BAND_CHOICES = {"computed", "provisional", "inventory", "all"}


def _validation_band(rule) -> str:
    if rule is None:
        return "inventory"
    band = rule_quality_band(rule)
    if band == "computed":
        return "gold" if getattr(rule, "confidence", "medium") == "high" else "validated"
    if band == "provisional":
        return "beta" if rule_has_algorithm(rule) else "research"
    return "inventory"


def _rule_meta(festival_id: str) -> dict:
    rule = get_rule_v4(festival_id)
    if rule is None:
        return {
            "quality_band": "inventory",
            "rule_status": "inventory",
            "rule_family": "content_inventory",
            "validation_band": "inventory",
            "source_evidence_ids": [],
            "has_algorithm": False,
        }

    return {
        "quality_band": rule_quality_band(rule),
        "rule_status": rule.status,
        "rule_family": rule.rule_family,
        "validation_band": _validation_band(rule),
        "source_evidence_ids": [rule.source],
        "has_algorithm": rule_has_algorithm(rule),
    }


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
    repo = get_repository()

    festivals = repo.search(search) if search else repo.get_all()

    if category:
        festivals = [f for f in festivals if f.category == category]

    if region:
        region_l = region.lower()
        festivals = [
            f for f in festivals if any(region_l in r.lower() for r in (f.regional_focus or []))
        ]

    if tradition:
        tradition_l = tradition.lower()
        festivals = [
            f
            for f in festivals
            if tradition_l in f.category.lower() or tradition_l in (f.who_celebrates or "").lower()
        ]

    quality_band = quality_band.lower().strip()
    if quality_band not in QUALITY_BAND_CHOICES:
        raise HTTPException(status_code=400, detail=f"Invalid quality_band '{quality_band}'")

    rule_meta = {festival.id: _rule_meta(festival.id) for festival in festivals}

    if quality_band != "all":
        festivals = [
            festival
            for festival in festivals
            if rule_meta.get(festival.id, {}).get("quality_band") == quality_band
        ]

    if algorithmic_only:
        festivals = [
            festival
            for festival in festivals
            if rule_meta.get(festival.id, {}).get("has_algorithm")
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

    # Convert to summaries with rule quality metadata
    summaries = []
    for festival in paginated:
        summary = repo.to_summary(festival)
        meta = rule_meta.get(festival.id) or _rule_meta(festival.id)
        summary.rule_status = meta["rule_status"]
        summary.rule_family = meta["rule_family"]
        summary.validation_band = meta["validation_band"]
        summary.source_evidence_ids = meta["source_evidence_ids"]
        summaries.append(summary)

    return FestivalListResponse(
        festivals=summaries,
        total=len(festivals),
        page=page,
        page_size=page_size,
        provenance=build_provenance(),
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
    coverage["provenance"] = build_provenance().model_dump()
    return coverage


@router.get("/coverage/scoreboard")
async def get_festival_coverage_scoreboard(
    target_rules: int = Query(300, ge=1, le=5000, description="Target computed-rule count"),
):
    """Return truth-first computed/provisional/inventory coverage scoreboard."""
    scoreboard = get_rules_scoreboard(target=target_rules)
    scoreboard["provenance"] = build_provenance().model_dump()
    return scoreboard


@router.get("/disputes", response_model=FestivalDisputeAtlasResponse)
async def get_dispute_atlas(
    year: int = Query(..., ge=2000, le=2200, description="Gregorian year"),
    limit: int = Query(18, ge=1, le=100, description="Maximum number of dispute/risk rows"),
):
    """Return authority conflicts and risk-ranked festival-year rows for truth/dispute surfaces."""
    repo = get_repository()
    disputes: list[FestivalDisputeRecord] = []

    for festival in sorted(repo.get_all(), key=lambda item: item.significance_level, reverse=True):
        dates, availability = repo.get_dates_with_availability(
            festival.id,
            year,
            authority_mode="authority_compare",
        )
        if not dates or (availability and availability.status != "available"):
            continue

        risk = build_risk_payload(
            start_date=dates.start_date,
            alternate_candidates=[candidate.model_dump() for candidate in dates.alternate_candidates],
            support_tier=dates.support_tier,
            fallback_used=dates.fallback_used,
        )
        if not dates.authority_conflict and risk["boundary_radar"] == "stable":
            continue

        disputes.append(
            FestivalDisputeRecord(
                festival_id=festival.id,
                festival_name=festival.name,
                year=year,
                start_date=dates.start_date,
                support_tier=dates.support_tier or "computed",
                source_family=dates.source_family,
                selection_policy=dates.selection_policy or "authority_compare",
                authority_conflict=dates.authority_conflict,
                alternate_candidates=dates.alternate_candidates,
                boundary_radar=risk["boundary_radar"],
                stability_score=risk["stability_score"],
                recommended_action=risk["recommended_action"],
                engine_path=dates.engine_path,
                fallback_used=dates.fallback_used,
            )
        )

    disputes.sort(
        key=lambda item: (
            0 if item.boundary_radar == "high_disagreement_risk" else 1,
            item.stability_score,
            item.festival_name,
        )
    )

    return FestivalDisputeAtlasResponse(
        year=year,
        total_items=len(disputes[:limit]),
        truth_ladder=truth_ladder(),
        disputes=disputes[:limit],
        provenance=build_provenance(year=year),
    )


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
    repo = get_repository()
    start = from_date or date.today()

    quality_band = quality_band.lower().strip()
    if quality_band not in QUALITY_BAND_CHOICES:
        raise HTTPException(status_code=400, detail=f"Invalid quality_band '{quality_band}'")

    results = []
    window_end = start + timedelta(days=days)
    if profile:
        occurrences = collect_profile_occurrences(repo, start, window_end, profile)
        for festival, dates, profile_note, _availability in occurrences:
            meta = _rule_meta(festival.id)
            if quality_band != "all" and meta["quality_band"] != quality_band:
                continue
            results.append(
                UpcomingFestival(
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
                    rule_status=meta["rule_status"],
                    rule_family=meta["rule_family"],
                    validation_band=meta["validation_band"],
                    source_evidence_ids=meta["source_evidence_ids"],
                    date_status="available",
                    date_status_note=profile_note
                    or "Resolved calendar dates are available for this upcoming occurrence.",
                    support_tier=dates.support_tier,
                    selection_policy=dates.selection_policy,
                    source_family=dates.source_family,
                    fallback_used=dates.fallback_used,
                    calibration_status=dates.calibration_status,
                    profile_id=profile,
                    profile_note=profile_note,
                )
            )
    else:
        upcoming = rule_service.upcoming(start, days=days)
        for festival_id, dates in upcoming:
            meta = _rule_meta(festival_id)
            if quality_band != "all" and meta["quality_band"] != quality_band:
                continue

            festival = repo.get_by_id(festival_id)
            override_info = (
                get_festival_override_info(
                    festival_id,
                    dates.year,
                    authority_mode="authority_compare",
                )
                if dates.method == "override"
                else None
            )
            authority_conflict = bool(
                override_info and int(override_info.get("candidate_count") or 1) > 1
            )
            rule_info = rule_service.info(festival_id)
            if festival:
                results.append(
                    UpcomingFestival(
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
                        rule_status=meta["rule_status"],
                        rule_family=meta["rule_family"],
                        validation_band=meta["validation_band"],
                        source_evidence_ids=meta["source_evidence_ids"],
                        date_status="available",
                        date_status_note=resolved_date_note(
                            festival_id,
                            dates.year,
                            dates.method,
                            "Resolved calendar dates are available for this upcoming occurrence.",
                        ),
                        support_tier=(
                            "conflicted"
                            if authority_conflict
                            else derive_support_tier(
                                confidence="official" if dates.method == "override" else "computed",
                                quality_band="validated"
                                if dates.method == "override"
                                else "computed",
                            )
                        ),
                        selection_policy="public_default",
                        source_family=(
                            (override_info or {}).get("source_family")
                            if dates.method == "override"
                            else (rule_info.source if rule_info else None)
                        ),
                        fallback_used=route_fallback_used(dates.method),
                        calibration_status=route_calibration_status(dates.method),
                    )
                )

    return UpcomingFestivalsResponse(
        festivals=results,
        from_date=start,
        to_date=window_end,
        total=len(results),
        provenance=build_provenance(),
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
    repo = get_repository()

    results = []
    if profile:
        occurrences = collect_profile_occurrences(repo, target_date, target_date, profile)
        for festival, dates, profile_note, _availability in occurrences:
            results.append(
                summary_for_occurrence(
                    repo,
                    festival,
                    dates,
                    profile,
                    profile_note,
                    "Resolved calendar dates are available for this day.",
                )
            )
    else:
        festivals_data = rule_service.on_date(target_date)
        for festival_id, dates in festivals_data:
            festival = repo.get_by_id(festival_id)
            if festival:
                summary = repo.to_summary(festival)
                summary.next_start = dates.start_date
                summary.next_end = dates.end_date
                summary.date_status = "available"
                summary.date_status_note = resolved_date_note(
                    festival_id,
                    dates.year,
                    dates.method,
                    "Resolved calendar dates are available for this day.",
                )
                results.append(summary)

    return results


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
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be 1-12")

    repo = get_repository()

    # Calculate first and last day of month
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)

    first_day = date(year, month, 1)
    last_day = next_month - timedelta(days=1)

    occurrence_map: dict[date, list[FestivalSummary]] = {}
    if profile:
        for festival, dates, profile_note, _availability in collect_profile_occurrences(
            repo, first_day, last_day, profile
        ):
            cursor = max(dates.start_date, first_day)
            cursor_end = min(dates.end_date, last_day)
            while cursor <= cursor_end:
                occurrence_map.setdefault(cursor, []).append(
                    summary_for_occurrence(
                        repo,
                        festival,
                        dates,
                        profile,
                        profile_note,
                        "Resolved calendar dates are available for this day.",
                    )
                )
                cursor += timedelta(days=1)

    days = []
    current = first_day

    while current <= last_day:
        # Get festivals on this day
        summaries = occurrence_map.get(current, [])
        if not profile:
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

        days.append(
            CalendarDayFestivals(
                date=current,
                bs_date=bs_str,
                festivals=summaries,
                tithi=tithi,
                paksha=paksha,
            )
        )

        current += timedelta(days=1)

    return FestivalCalendarResponse(
        days=days,
        month=month,
        year=year,
        provenance=build_provenance(),
    )


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
    repo = get_repository()
    authority_mode = validate_authority_mode(authority_mode)

    festival = repo.get_by_id(festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail=f"Festival '{festival_id}' not found")

    # Get dates for specified year or current/next occurrence
    target_year = year or date.today().year
    dates, date_availability = repo.get_dates_with_availability(
        festival_id,
        target_year,
        authority_mode=authority_mode,
    )

    if not dates and not year:
        # Try next year
        fallback_year = target_year + 1
        fallback_dates, fallback_availability = repo.get_dates_with_availability(
            festival_id,
            fallback_year,
            authority_mode=authority_mode,
        )
        if fallback_dates is not None:
            dates = fallback_dates
            date_availability = FestivalDateAvailability(
                status="available",
                note="The current year's occurrence was unavailable or already passed, so the next resolved occurrence is shown.",
                requested_year=target_year,
                resolved_year=fallback_year,
            )
        else:
            date_availability = fallback_availability

    dates, profile_note = apply_profile_variant_to_dates(festival_id, target_year, dates, profile)
    if profile_note and date_availability and date_availability.status == "available":
        date_availability = date_availability.model_copy(update={"note": profile_note})

    if not dates:
        # No dates available - don't fake it, let frontend handle gracefully
        dates = None
    else:
        risk = build_risk_payload(
            start_date=dates.start_date,
            alternate_candidates=[candidate.model_dump() for candidate in dates.alternate_candidates],
            support_tier=dates.support_tier,
            fallback_used=dates.fallback_used,
            risk_mode=risk_mode,
        )
        dates = dates.model_copy(update=risk)

    # Canonical ritual schema for UI contract: ritual_sequence.days[]
    ritual_sequence = normalize_ritual_sequence(festival)
    if ritual_sequence:
        festival = festival.model_copy(update={"ritual_sequence": ritual_sequence})

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
        date_availability=date_availability,
        nearby_festivals=nearby[:4] if nearby else None,
        completeness=build_detail_completeness(
            festival,
            dates=dates,
            date_availability=date_availability,
            nearby=nearby[:4] if nearby else [],
        ),
        provenance=build_provenance(festival_id=festival_id, year=target_year),
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
