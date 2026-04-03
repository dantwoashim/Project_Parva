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
from ..explainability import create_reason_trace
from ..provenance import get_latest_snapshot_id, get_provenance_payload
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
from .models import (
    BSDateLite,
    CalendarDayFestivals,
    FestivalCalendarResponse,
    FestivalDateAvailability,
    FestivalDates,
    FestivalDetailResponse,
    FestivalExplainResponse,
    FestivalListResponse,
    FestivalSummary,
    ProvenanceMeta,
    UpcomingFestival,
    UpcomingFestivalsResponse,
)
from .repository import get_repository

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


def _build_provenance(
    festival_id: Optional[str] = None,
    year: Optional[int] = None,
) -> ProvenanceMeta:
    snapshot_id = get_latest_snapshot_id()
    verify_url = "/v3/api/provenance/root"
    if festival_id and year and snapshot_id:
        verify_url = (
            f"/v3/api/provenance/proof?festival={festival_id}&year={year}&snapshot={snapshot_id}"
        )
    return ProvenanceMeta(**get_provenance_payload(verify_url=verify_url, create_if_missing=True))


def _resolved_date_note(festival_id: str, year: int, method: str, default_note: str) -> str:
    if method != "override":
        return default_note
    info = get_festival_override_info(festival_id, year)
    if not info or int(info.get("candidate_count") or 1) <= 1:
        return default_note
    source = info.get("source") or "override source"
    return (
        f"{default_note} Multiple authority candidates exist for this festival-year; "
        f"the current default keeps {info['start'].isoformat()} from {source}."
    )


def _profile_map() -> dict[str, dict]:
    return {
        str(profile.get("profile_id")): profile
        for profile in list_profiles()
        if profile.get("profile_id")
    }


def _validate_profile(profile_id: Optional[str]) -> Optional[dict]:
    if not profile_id:
        return None
    profile = _profile_map().get(profile_id)
    if profile is None:
        raise HTTPException(status_code=400, detail=f"Unknown profile '{profile_id}'")
    return profile


def _to_bs_lite(target: date) -> BSDateLite:
    bs_year, bs_month, bs_day = gregorian_to_bs(target)
    month_name = get_bs_month_name(bs_month)
    return BSDateLite(
        year=bs_year,
        month=bs_month,
        day=bs_day,
        month_name=month_name,
        formatted=f"{bs_year} {month_name} {bs_day}",
    )


def _apply_profile_variant_to_dates(
    festival_id: str,
    year: int,
    dates: Optional[FestivalDates],
    profile_id: Optional[str],
) -> tuple[Optional[FestivalDates], Optional[str]]:
    profile = _validate_profile(profile_id)
    if dates is None or profile is None:
        return dates, None

    variants = filter_variants_by_profile(calculate_with_variants(festival_id, year), profile_id)
    if not variants:
        note = (
            f"No dedicated {profile_id} variant is published for this festival-year, "
            f"so the default date is shown."
        )
        return (
            dates.model_copy(
                update={
                    "profile_id": profile_id,
                    "profile_tradition": profile.get("tradition"),
                    "profile_region": profile.get("region"),
                    "profile_note": note,
                }
            ),
            note,
        )

    variant = variants[0]
    start = date.fromisoformat(variant["date"])
    end = date.fromisoformat(variant["end_date"])
    if start == dates.start_date and end == dates.end_date:
        note = variant.get("notes") or f"{profile_id} aligns with the default festival date."
    else:
        note = variant.get("notes") or f"{profile_id} applies a documented regional/tradition shift."

    updated = dates.model_copy(
        update={
            "start_date": start,
            "end_date": end,
            "duration_days": (end - start).days + 1,
            "bs_start": _to_bs_lite(start),
            "bs_end": _to_bs_lite(end),
            "days_until": (start - date.today()).days if (start - date.today()).days >= 0 else None,
            "profile_id": profile_id,
            "profile_tradition": profile.get("tradition"),
            "profile_region": profile.get("region"),
            "profile_note": note,
        }
    )
    return updated, note


def _collect_profile_occurrences(
    repo,
    start: date,
    end: date,
    profile_id: Optional[str],
) -> list[tuple[Festival, FestivalDates, Optional[str], FestivalDateAvailability]]:
    _validate_profile(profile_id)
    year_start = start.year - 1
    year_end = end.year + 1
    seen: set[tuple[str, date, date]] = set()
    occurrences: list[tuple[Festival, FestivalDates, Optional[str], FestivalDateAvailability]] = []

    for festival in repo.get_all():
        for year in range(year_start, year_end + 1):
            dates, availability = repo.get_dates_with_availability(festival.id, year)
            if not dates:
                continue

            adjusted_dates, profile_note = _apply_profile_variant_to_dates(
                festival.id, year, dates, profile_id
            )
            if adjusted_dates is None:
                continue
            if adjusted_dates.end_date < start or adjusted_dates.start_date > end:
                continue

            key = (festival.id, adjusted_dates.start_date, adjusted_dates.end_date)
            if key in seen:
                continue
            seen = seen | {key}
            occurrences.append((festival, adjusted_dates, profile_note, availability))

    occurrences.sort(key=lambda item: (item[1].start_date, item[0].id))
    return occurrences


def _summary_for_occurrence(
    repo,
    festival: Festival,
    dates: FestivalDates,
    profile_id: Optional[str],
    profile_note: Optional[str],
    default_note: str,
) -> FestivalSummary:
    summary = repo.to_summary(festival)
    summary.next_start = dates.start_date
    summary.next_end = dates.end_date
    summary.days_until = (dates.start_date - date.today()).days
    summary.date_status = "available"
    summary.date_status_note = profile_note or default_note
    summary.profile_id = profile_id
    summary.profile_note = profile_note
    return summary


def _completeness_section(status: str, note: str) -> dict[str, str]:
    return {"status": status, "note": note}


def _build_detail_completeness(
    festival,
    *,
    dates: Optional[FestivalDates],
    date_availability: Optional[FestivalDateAvailability],
    nearby: list[FestivalSummary],
) -> dict[str, object]:
    mythology = festival.mythology
    has_summary_narrative = bool(
        mythology and (mythology.summary or mythology.origin_story or mythology.historical_context)
    )
    has_deep_narrative = bool(
        mythology
        and (
            mythology.origin_story
            or mythology.historical_context
            or mythology.legends
            or mythology.scriptural_references
            or mythology.regional_variations
        )
    )

    if has_summary_narrative and has_deep_narrative:
        narrative = _completeness_section(
            "available",
            "Editorial origin, meaning, and contextual notes are published for this observance.",
        )
    elif festival.description or has_summary_narrative:
        narrative = _completeness_section(
            "partial",
            "A summary is available, but the deeper editorial origin story is still partial.",
        )
    else:
        narrative = _completeness_section(
            "missing",
            "Editorial origin material has not been published for this observance yet.",
        )

    ritual_days = festival.ritual_sequence.get("days", []) if isinstance(festival.ritual_sequence, dict) else []
    has_canonical_rituals = bool(ritual_days)
    has_source_rituals = bool(festival.daily_rituals or festival.simple_rituals)
    if has_canonical_rituals:
        ritual_sequence = _completeness_section(
            "available",
            "Structured ritual steps are published for this observance.",
        )
    elif has_source_rituals:
        ritual_sequence = _completeness_section(
            "partial",
            "Source ritual material exists, but the canonical step-by-step timeline is still being normalized.",
        )
    else:
        ritual_sequence = _completeness_section(
            "missing",
            "Structured ritual steps are not part of the live profile for this observance yet.",
        )

    if dates is not None:
        date_resolution = _completeness_section(
            "available",
            "Resolved calendar dates are available for the requested year.",
        )
    elif date_availability and date_availability.status == "missing_rule":
        date_resolution = _completeness_section(
            "missing",
            "No computed rule is published for this observance yet, so live dates cannot be resolved.",
        )
    elif date_availability and date_availability.status == "calculation_error":
        date_resolution = _completeness_section(
            "partial",
            "A rule exists, but the date engine failed while resolving the requested year.",
        )
    else:
        date_resolution = _completeness_section(
            "missing",
            "Resolved calendar dates are not available for the requested year.",
        )

    if nearby:
        related_observances = _completeness_section(
            "available",
            "Nearby observances are available for the current ritual window.",
        )
    elif festival.related_festivals:
        related_observances = _completeness_section(
            "partial",
            "Editorial related observances are known, but the live nearby calendar window did not return companion festivals.",
        )
    else:
        related_observances = _completeness_section(
            "missing",
            "No nearby observances were returned for this festival window.",
        )

    statuses = [
        narrative["status"],
        ritual_sequence["status"],
        date_resolution["status"],
        related_observances["status"],
    ]
    if festival.content_status == "complete" and "missing" not in statuses:
        overall = "complete"
    elif "available" in statuses or "partial" in statuses:
        overall = "partial"
    else:
        overall = "minimal"

    return {
        "overall": overall,
        "narrative": narrative,
        "ritual_sequence": ritual_sequence,
        "dates": date_resolution,
        "related_observances": related_observances,
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


@router.get("/coverage/scoreboard")
async def get_festival_coverage_scoreboard(
    target_rules: int = Query(300, ge=1, le=5000, description="Target computed-rule count"),
):
    """Return truth-first computed/provisional/inventory coverage scoreboard."""
    scoreboard = get_rules_scoreboard(target=target_rules)
    scoreboard["provenance"] = _build_provenance().model_dump()
    return scoreboard


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
        occurrences = _collect_profile_occurrences(repo, start, window_end, profile)
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
                        date_status_note=_resolved_date_note(
                            festival_id,
                            dates.year,
                            dates.method,
                            "Resolved calendar dates are available for this upcoming occurrence.",
                        ),
                    )
                )

    return UpcomingFestivalsResponse(
        festivals=results,
        from_date=start,
        to_date=window_end,
        total=len(results),
        provenance=_build_provenance(),
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
        occurrences = _collect_profile_occurrences(repo, target_date, target_date, profile)
        for festival, dates, profile_note, _availability in occurrences:
            results.append(
                _summary_for_occurrence(
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
                summary.date_status_note = _resolved_date_note(
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
    last_day = next_month - __import__("datetime").timedelta(days=1)

    occurrence_map: dict[date, list[FestivalSummary]] = {}
    if profile:
        for festival, dates, profile_note, _availability in _collect_profile_occurrences(
            repo, first_day, last_day, profile
        ):
            cursor = max(dates.start_date, first_day)
            cursor_end = min(dates.end_date, last_day)
            while cursor <= cursor_end:
                occurrence_map.setdefault(cursor, []).append(
                    _summary_for_occurrence(
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

        current += __import__("datetime").timedelta(days=1)

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
    profile: Optional[str] = Query(None, description="Variant profile id"),
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
    dates, date_availability = repo.get_dates_with_availability(festival_id, target_year)

    if not dates and not year:
        # Try next year
        fallback_year = target_year + 1
        fallback_dates, fallback_availability = repo.get_dates_with_availability(
            festival_id, fallback_year
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

    dates, profile_note = _apply_profile_variant_to_dates(festival_id, target_year, dates, profile)
    if profile_note and date_availability and date_availability.status == "available":
        date_availability = date_availability.model_copy(update={"note": profile_note})

    if not dates:
        # No dates available - don't fake it, let frontend handle gracefully
        dates = None

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
        completeness=_build_detail_completeness(
            festival,
            dates=dates,
            date_availability=date_availability,
            nearby=nearby[:4] if nearby else [],
        ),
        provenance=_build_provenance(festival_id=festival_id, year=target_year),
    )


@router.get("/{festival_id}/explain", response_model=FestivalExplainResponse)
async def explain_festival_date(
    festival_id: str,
    year: Optional[int] = Query(None, description="Gregorian year for explanation"),
    profile: Optional[str] = Query(None, description="Variant profile id"),
):
    """
    Explain why a festival resolves to a specific date in the selected year.
    """
    repo = get_repository()
    festival = repo.get_by_id(festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail=f"Festival '{festival_id}' not found")

    target_year = year or date.today().year
    selected_profile = _validate_profile(profile)
    date_result = rule_service.calculate(festival_id, target_year)
    if not date_result:
        raise HTTPException(
            status_code=404, detail=f"Could not calculate '{festival_id}' for {target_year}"
        )

    rule = rule_service.info(festival_id)
    structured_steps = []
    if rule and getattr(rule, "type", None) == "lunar":
        rule_summary = f"{rule.lunar_month} {str(rule.paksha).capitalize()} {rule.tithi}"
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
                "input": {
                    "bs_month": getattr(rule, "bs_month", None),
                    "solar_day": getattr(rule, "solar_day", None),
                },
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
                "output": {
                    "start_date": date_result.start_date.isoformat(),
                    "method": "fallback_v1",
                },
                "rule_id": festival_id,
                "source": "calculator.py",
                "math_expression": None,
            }
        ]

    override_info = get_festival_override_info(festival_id, target_year)
    if date_result.method == "override" and override_info and override_info.get("candidate_count", 1) > 1:
        candidate_count = int(override_info["candidate_count"])
        steps.append(
            f"Authority review found {candidate_count} candidate date entries for this festival-year; "
            f"the current default keeps {override_info['start'].isoformat()}."
        )
        structured_steps.append(
            {
                "step_type": "authority_conflict",
                "input": {"candidate_count": candidate_count},
                "output": {
                    "selected_start_date": override_info["start"].isoformat(),
                },
                "rule_id": festival_id,
                "source": "ground_truth_overrides+ground_truth",
                "math_expression": None,
            }
        )
        explanation += (
            f" Multiple authority candidates exist for this festival-year, and the current "
            f"default override keeps {override_info['start'].isoformat()}."
        )
        if override_info.get("suggested_profile_id") and override_info.get("suggested_start"):
            suggested_profile_id = str(override_info["suggested_profile_id"])
            suggested_start = override_info["suggested_start"].isoformat()
            suggested_reason = override_info.get("suggested_reason") or (
                f"Use {suggested_profile_id} to inspect the alternate authority-backed date."
            )
            steps.append(
                f"An alternate authority-backed path is available via profile "
                f"{suggested_profile_id}, which resolves to {suggested_start}."
            )
            explanation += f" {suggested_reason}"

    profile_note = None
    if selected_profile is not None:
        variants = filter_variants_by_profile(calculate_with_variants(festival_id, target_year), profile)
        if variants:
            variant = variants[0]
            date_result.start_date = date.fromisoformat(variant["date"])
            date_result.end_date = date.fromisoformat(variant["end_date"])
            profile_note = variant.get("notes") or f"{profile} applies a documented profile variant."
            steps.append(
                f"Apply profile variant for {profile}, resolving the observance to {date_result.start_date.isoformat()}."
            )
            structured_steps.append(
                {
                    "step_type": "profile_variant",
                    "input": {"profile_id": profile},
                    "output": {"start_date": date_result.start_date.isoformat()},
                    "rule_id": festival_id,
                    "source": "regional_map.json",
                    "math_expression": None,
                }
            )
            explanation += f" Under the {profile} profile, the observance resolves to {date_result.start_date.isoformat()}."
        else:
            profile_note = (
                f"No dedicated {profile} variant is published for this festival-year, so the default date is shown."
            )
            explanation += f" {profile_note}"

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
        profile_id=profile,
        profile_note=profile_note,
        authority_suggested_profile_id=override_info.get("suggested_profile_id")
        if override_info
        else None,
        authority_suggested_start_date=override_info.get("suggested_start")
        if override_info
        else None,
        authority_suggested_reason=override_info.get("suggested_reason") if override_info else None,
        provenance=_build_provenance(festival_id=festival_id, year=target_year),
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
    _validate_profile(profile)
    results = []

    for year in range(start, start + years):
        dates, availability = repo.get_dates_with_availability(festival_id, year)
        if dates:
            dates, _profile_note = _apply_profile_variant_to_dates(festival_id, year, dates, profile)
            dates.provenance = _build_provenance(festival_id=festival_id, year=year)
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
        "provenance": _build_provenance(festival_id=festival_id, year=year),
    }
