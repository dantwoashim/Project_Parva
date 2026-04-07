"""Application-layer use cases for festival route surfaces."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from fastapi import HTTPException

from ..calendar import calculate_tithi, get_bs_month_name, gregorian_to_bs
from ..calendar.overrides import get_festival_override_info
from ..core.request_context import derive_support_tier
from ..rules import get_rule_service
from ..rules.catalog_v4 import (
    get_rule_v4,
    get_rules_coverage,
    get_rules_scoreboard,
    rule_has_algorithm,
    rule_quality_band,
)
from ..services.ritual_normalization import normalize_ritual_sequence
from .detail_service import build_detail_completeness
from .models import (
    CalendarDayFestivals,
    FestivalCalendarResponse,
    FestivalDateAvailability,
    FestivalDetailResponse,
    FestivalDisputeAtlasResponse,
    FestivalDisputeRecord,
    FestivalListResponse,
    UpcomingFestival,
    UpcomingFestivalsResponse,
)
from .presenters import (
    present_dispute_atlas,
    present_festival_calendar,
    present_festival_detail,
    present_festival_list,
    present_upcoming_festivals,
)
from .query_service import (
    apply_profile_variant_to_dates,
    collect_profile_occurrences,
    resolved_date_note,
    summary_for_occurrence,
)
from .query_service import (
    calibration_status as route_calibration_status,
)
from .query_service import (
    fallback_used as route_fallback_used,
)
from .repository import get_repository
from .risk_service import build_risk_payload, truth_ladder
from .trust import build_provenance

QUALITY_BAND_CHOICES = {"computed", "provisional", "inventory", "all"}
rule_service = get_rule_service()


def _validation_band(rule) -> str:
    if rule is None:
        return "inventory"
    band = rule_quality_band(rule)
    if band == "computed":
        return "gold" if getattr(rule, "confidence", "medium") == "high" else "validated"
    if band == "provisional":
        return "beta" if rule_has_algorithm(rule) else "research"
    return "inventory"


def rule_meta(festival_id: str) -> dict:
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


def list_festivals_payload(
    *,
    category: Optional[str],
    search: Optional[str],
    region: Optional[str],
    tradition: Optional[str],
    source: Optional[str],
    quality_band: str,
    algorithmic_only: bool,
    page: int,
    page_size: int,
) -> FestivalListResponse:
    repo = get_repository()
    festivals = repo.search(search) if search else repo.get_all()

    if category:
        festivals = [f for f in festivals if f.category == category]
    if region:
        region_l = region.lower()
        festivals = [f for f in festivals if any(region_l in r.lower() for r in (f.regional_focus or []))]
    if tradition:
        tradition_l = tradition.lower()
        festivals = [
            f for f in festivals if tradition_l in f.category.lower() or tradition_l in (f.who_celebrates or "").lower()
        ]

    quality_band = quality_band.lower().strip()
    if quality_band not in QUALITY_BAND_CHOICES:
        raise HTTPException(status_code=400, detail=f"Invalid quality_band '{quality_band}'")

    meta_by_festival = {festival.id: rule_meta(festival.id) for festival in festivals}
    if quality_band != "all":
        festivals = [festival for festival in festivals if meta_by_festival.get(festival.id, {}).get("quality_band") == quality_band]
    if algorithmic_only:
        festivals = [festival for festival in festivals if meta_by_festival.get(festival.id, {}).get("has_algorithm")]
    if source:
        source_l = source.lower()
        festivals = [
            festival
            for festival in festivals
            if (rule := get_rule_v4(festival.id)) and source_l in rule.source.lower()
        ]

    festivals.sort(key=lambda f: f.significance_level, reverse=True)
    paginated = festivals[(page - 1) * page_size : (page - 1) * page_size + page_size]
    summaries = []
    for festival in paginated:
        summary = repo.to_summary(festival)
        meta = meta_by_festival.get(festival.id) or rule_meta(festival.id)
        summary.rule_status = meta["rule_status"]
        summary.rule_family = meta["rule_family"]
        summary.validation_band = meta["validation_band"]
        summary.source_evidence_ids = meta["source_evidence_ids"]
        summaries.append(summary)
    return present_festival_list(
        festivals=summaries,
        total=len(festivals),
        page=page,
        page_size=page_size,
        provenance=build_provenance(),
    )


def dispute_atlas_payload(*, year: int, limit: int) -> FestivalDisputeAtlasResponse:
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
    return present_dispute_atlas(
        year=year,
        disputes=disputes[:limit],
        truth_ladder=truth_ladder(),
        provenance=build_provenance(year=year),
    )


def upcoming_festivals_payload(
    *,
    days: int,
    from_date: Optional[date],
    quality_band: str,
    profile: Optional[str],
) -> UpcomingFestivalsResponse:
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
            meta = rule_meta(festival.id)
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
        for festival_id, dates in rule_service.upcoming(start, days=days):
            meta = rule_meta(festival_id)
            if quality_band != "all" and meta["quality_band"] != quality_band:
                continue
            festival = repo.get_by_id(festival_id)
            override_info = (
                get_festival_override_info(festival_id, dates.year, authority_mode="authority_compare")
                if dates.method == "override"
                else None
            )
            authority_conflict = bool(override_info and int(override_info.get("candidate_count") or 1) > 1)
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
                                quality_band="validated" if dates.method == "override" else "computed",
                            )
                        ),
                        selection_policy="public_default",
                        source_family=((override_info or {}).get("source_family") if dates.method == "override" else (rule_info.source if rule_info else None)),
                        fallback_used=route_fallback_used(dates.method),
                        calibration_status=route_calibration_status(dates.method),
                    )
                )
    return present_upcoming_festivals(
        festivals=results,
        from_date=start,
        to_date=window_end,
        provenance=build_provenance(),
    )


def festivals_on_date_payload(*, target_date: date, profile: Optional[str]):
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
        for festival_id, dates in rule_service.on_date(target_date):
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


def calendar_month_payload(*, year: int, month: int, profile: Optional[str]) -> FestivalCalendarResponse:
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be 1-12")

    repo = get_repository()
    next_month = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    first_day = date(year, month, 1)
    last_day = next_month - timedelta(days=1)

    occurrence_map: dict[date, list] = {}
    if profile:
        for festival, dates, profile_note, _availability in collect_profile_occurrences(repo, first_day, last_day, profile):
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
        summaries = occurrence_map.get(current, [])
        if not profile:
            summaries = []
            for festival_id, dates in rule_service.on_date(current):
                festival = repo.get_by_id(festival_id)
                if festival:
                    summaries.append(repo.to_summary(festival))
        try:
            tithi_info = calculate_tithi(current)
            tithi = tithi_info.get("display_number")
            paksha = tithi_info.get("paksha")
            _bs_year, bs_month, bs_day = gregorian_to_bs(current)
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
    return present_festival_calendar(
        days=days,
        month=month,
        year=year,
        provenance=build_provenance(),
    )


def festival_detail_payload(
    *,
    festival_id: str,
    year: Optional[int],
    profile: Optional[str],
    authority_mode: str,
    risk_mode: str,
) -> FestivalDetailResponse:
    repo = get_repository()
    festival = repo.get_by_id(festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail=f"Festival '{festival_id}' not found")
    target_year = year or date.today().year
    dates, date_availability = repo.get_dates_with_availability(
        festival_id,
        target_year,
        authority_mode=authority_mode,
    )
    if not dates and not year:
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

    if dates:
        risk = build_risk_payload(
            start_date=dates.start_date,
            alternate_candidates=[candidate.model_dump() for candidate in dates.alternate_candidates],
            support_tier=dates.support_tier,
            fallback_used=dates.fallback_used,
            risk_mode=risk_mode,
        )
        dates = dates.model_copy(update=risk)

    ritual_sequence = normalize_ritual_sequence(festival)
    if ritual_sequence:
        festival = festival.model_copy(update={"ritual_sequence": ritual_sequence})

    nearby = []
    if dates:
        search_start = dates.start_date - timedelta(days=15)
        for fid, fdates in rule_service.upcoming(search_start, days=45)[:5]:
            if fid != festival_id:
                f = repo.get_by_id(fid)
                if f:
                    nearby.append(repo.to_summary(f))

    return present_festival_detail(
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


def coverage_payload(*, target_rules: int) -> dict:
    repo = get_repository()
    coverage = get_rules_coverage(target=target_rules)
    content_count = len(repo.get_all())
    coverage["festival_content_count"] = content_count
    coverage["content_rule_gap"] = max(coverage["total_rules"] - content_count, 0)
    coverage["provenance"] = build_provenance().model_dump()
    return coverage


def coverage_scoreboard_payload(*, target_rules: int) -> dict:
    scoreboard = get_rules_scoreboard(target=target_rules)
    scoreboard["provenance"] = build_provenance().model_dump()
    return scoreboard
