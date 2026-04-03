"""Festival query helpers shared by route handlers."""

from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import HTTPException

from ..calendar import get_bs_month_name, gregorian_to_bs
from ..calendar.overrides import AUTHORITY_MODE_CHOICES, get_festival_override_info
from ..rules.variants import calculate_with_variants, filter_variants_by_profile, list_profiles
from .models import BSDateLite, Festival, FestivalDateAvailability, FestivalDates, FestivalSummary


def validate_authority_mode(authority_mode: str) -> str:
    normalized = str(authority_mode or "public_default").strip().lower()
    if normalized not in AUTHORITY_MODE_CHOICES:
        raise HTTPException(status_code=400, detail=f"Invalid authority_mode '{authority_mode}'")
    return normalized


def fallback_used(method: str) -> bool:
    normalized = str(method or "").lower()
    return "fallback" in normalized or "legacy" in normalized


def calibration_status(method: str) -> str:
    return "not_applicable" if method == "override" else "unavailable"


def resolved_date_note(festival_id: str, year: int, method: str, default_note: str) -> str:
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


def profile_map() -> dict[str, dict]:
    return {
        str(profile.get("profile_id")): profile
        for profile in list_profiles()
        if profile.get("profile_id")
    }


def validate_profile(profile_id: Optional[str]) -> Optional[dict]:
    if not profile_id:
        return None
    profile = profile_map().get(profile_id)
    if profile is None:
        raise HTTPException(status_code=400, detail=f"Unknown profile '{profile_id}'")
    return profile


def to_bs_lite(target: date) -> BSDateLite:
    bs_year, bs_month, bs_day = gregorian_to_bs(target)
    month_name = get_bs_month_name(bs_month)
    return BSDateLite(
        year=bs_year,
        month=bs_month,
        day=bs_day,
        month_name=month_name,
        formatted=f"{bs_year} {month_name} {bs_day}",
    )


def apply_profile_variant_to_dates(
    festival_id: str,
    year: int,
    dates: Optional[FestivalDates],
    profile_id: Optional[str],
) -> tuple[Optional[FestivalDates], Optional[str]]:
    profile = validate_profile(profile_id)
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
            "bs_start": to_bs_lite(start),
            "bs_end": to_bs_lite(end),
            "days_until": (start - date.today()).days if (start - date.today()).days >= 0 else None,
            "profile_id": profile_id,
            "profile_tradition": profile.get("tradition"),
            "profile_region": profile.get("region"),
            "profile_note": note,
        }
    )
    return updated, note


def collect_profile_occurrences(
    repo,
    start: date,
    end: date,
    profile_id: Optional[str],
) -> list[tuple[Festival, FestivalDates, Optional[str], FestivalDateAvailability]]:
    validate_profile(profile_id)
    year_start = start.year - 1
    year_end = end.year + 1
    seen: set[tuple[str, date, date]] = set()
    occurrences: list[tuple[Festival, FestivalDates, Optional[str], FestivalDateAvailability]] = []

    for festival in repo.get_all():
        for year in range(year_start, year_end + 1):
            dates, availability = repo.get_dates_with_availability(festival.id, year)
            if not dates:
                continue

            adjusted_dates, profile_note = apply_profile_variant_to_dates(
                festival.id, year, dates, profile_id
            )
            if adjusted_dates is None:
                continue
            if adjusted_dates.end_date < start or adjusted_dates.start_date > end:
                continue

            key = (festival.id, adjusted_dates.start_date, adjusted_dates.end_date)
            if key in seen:
                continue
            seen.add(key)
            occurrences.append((festival, adjusted_dates, profile_note, availability))

    occurrences.sort(key=lambda item: (item[1].start_date, item[0].id))
    return occurrences


def summary_for_occurrence(
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


__all__ = [
    "apply_profile_variant_to_dates",
    "calibration_status",
    "collect_profile_occurrences",
    "fallback_used",
    "profile_map",
    "resolved_date_note",
    "summary_for_occurrence",
    "to_bs_lite",
    "validate_authority_mode",
    "validate_profile",
]
