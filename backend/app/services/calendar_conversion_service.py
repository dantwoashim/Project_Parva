"""Application-layer use cases for calendar conversion surfaces."""

from __future__ import annotations

from datetime import date
from typing import Any, Optional

from fastapi import HTTPException

from app.calendar.bikram_sambat import (
    bs_to_gregorian,
    get_bs_confidence,
    get_bs_estimated_error_days,
    get_bs_month_name,
    get_bs_source_range,
    get_bs_year_confidence,
    gregorian_to_bs,
    gregorian_to_bs_estimated,
    gregorian_to_bs_official,
)
from app.calendar.constants import BS_MAX_YEAR, BS_MIN_YEAR
from app.calendar.nepal_sambat import format_ns_date, get_current_ns_year
from app.domain.temporal_context import CalendarContext
from app.policy import get_policy_metadata
from app.services.calendar_presenters import present_calendar_payload
from app.services.trust_surface_service import build_surface_meta, build_surface_provenance
from app.uncertainty import build_bs_uncertainty


def parse_iso_date(date_str: str) -> date:
    try:
        parts = date_str.split("-")
        return date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError) as exc:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD") from exc


def _calendar_context(target_date: date, *, surface: str, support_tier: str | None = None) -> CalendarContext:
    return CalendarContext(target_date=target_date, surface=surface, support_tier=support_tier)


def _bs_support_meta(
    *,
    engine_path: str,
    confidence: str,
    uncertainty: dict[str, Any] | None,
    fallback_used: bool = False,
) -> dict[str, Any]:
    quality_band = "validated" if confidence == "official" else "provisional"
    return build_surface_meta(
        engine_path=engine_path,
        confidence=confidence,
        quality_band=quality_band,
        uncertainty=uncertainty,
        fallback_used=fallback_used,
    )


def bs_struct(gregorian_date: date) -> dict[str, Any]:
    bs_year, bs_month, bs_day = gregorian_to_bs(gregorian_date)
    month_name = get_bs_month_name(bs_month)
    return {
        "year": bs_year,
        "month": bs_month,
        "day": bs_day,
        "month_name": month_name,
        "formatted": f"{bs_year} {month_name} {bs_day}",
    }


def build_bs_date_payload(gregorian_date: date) -> dict[str, Any]:
    bs_year, bs_month, bs_day = gregorian_to_bs(gregorian_date)
    confidence = get_bs_confidence(gregorian_date)
    estimated_error_days = get_bs_estimated_error_days(gregorian_date)
    return {
        "year": bs_year,
        "month": bs_month,
        "day": bs_day,
        "month_name": get_bs_month_name(bs_month),
        "formatted": f"{bs_year} {get_bs_month_name(bs_month)} {bs_day}",
        "confidence": confidence,
        "source_range": get_bs_source_range(gregorian_date),
        "estimated_error_days": estimated_error_days,
        "uncertainty": build_bs_uncertainty(confidence, estimated_error_days),
    }


def build_ns_date_payload(gregorian_date: date) -> Optional[dict[str, Any]]:
    try:
        ns_year = get_current_ns_year(gregorian_date)
        return {
            "year": ns_year,
            "formatted": format_ns_date(gregorian_date),
        }
    except (ValueError, TypeError):
        return None


def build_tithi_payload(gregorian_date: date) -> dict[str, Any]:
    from app.calendar.ephemeris.swiss_eph import calculate_sunrise
    from app.calendar.ephemeris.time_utils import to_nepal_time
    from app.calendar.tithi import calculate_tithi, get_moon_phase_name, get_udaya_tithi
    from app.uncertainty import build_tithi_uncertainty

    try:
        udaya = get_udaya_tithi(gregorian_date)
        sunrise_utc = calculate_sunrise(gregorian_date)
        return {
            "tithi": udaya["tithi"],
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
    except (KeyError, TypeError, ValueError, RuntimeError):
        tithi_data = calculate_tithi(gregorian_date)
        return {
            "tithi": tithi_data["display_number"],
            "paksha": tithi_data["paksha"],
            "tithi_name": tithi_data["name"],
            "moon_phase": get_moon_phase_name(gregorian_date),
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


def build_conversion_payload(gregorian_date: date) -> dict[str, Any]:
    bs_payload = build_bs_date_payload(gregorian_date)
    tithi_payload = build_tithi_payload(gregorian_date)
    meta = build_surface_meta(
        engine_path=str(tithi_payload.get("method") or "calendar_conversion_v3"),
        confidence="estimated"
        if bs_payload.get("confidence") == "estimated"
        else str(tithi_payload.get("confidence") or "computed"),
        quality_band="validated",
        uncertainty=tithi_payload.get("uncertainty"),
    )
    context = _calendar_context(gregorian_date, surface="conversion", support_tier=str(meta["support_tier"]))
    return present_calendar_payload(
        body={
            "gregorian": gregorian_date.isoformat(),
            "bikram_sambat": bs_payload,
            "nepal_sambat": build_ns_date_payload(gregorian_date),
            "tithi": tithi_payload,
        },
        trust=meta,
        extra={
            "engine_version": "v3",
            "provenance": build_surface_provenance(calendar_context=context),
            "policy": get_policy_metadata(),
        },
    )


def build_compare_conversion_payload(gregorian_date: date) -> dict[str, Any]:
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
    except ValueError:
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
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    match = None
    if official:
        match = official["year"] == estimated["year"] and official["month"] == estimated["month"] and official["day"] == estimated["day"]

    meta = build_surface_meta(
        engine_path="bs_compare_official_vs_estimated",
        confidence="estimated" if official is None or match is False else "computed",
        quality_band="validated",
        uncertainty=(estimated or {}).get("uncertainty"),
        fallback_used=official is None,
    )
    context = _calendar_context(gregorian_date, surface="conversion_compare", support_tier=str(meta["support_tier"]))
    return present_calendar_payload(
        body={
            "gregorian": gregorian_date.isoformat(),
            "official": official,
            "estimated": estimated,
            "match": match,
        },
        trust=meta,
        extra={
            "engine_version": "v3",
            "provenance": build_surface_provenance(calendar_context=context),
            "policy": get_policy_metadata(),
        },
    )


def build_dual_month_payload(year: int, month: int) -> dict[str, Any]:
    current_year = date.today().year
    min_year = current_year - 200
    max_year = current_year + 200
    if year < min_year or year > max_year:
        raise HTTPException(
            status_code=400,
            detail=f"Year must be between {min_year} and {max_year} for the ±200 year calendar explorer",
        )
    month_start = date(year, month, 1)
    next_month = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    rows = []
    cursor = month_start
    while cursor < next_month:
        rows.append(
            {
                "gregorian": {
                    "iso": cursor.isoformat(),
                    "year": cursor.year,
                    "month": cursor.month,
                    "day": cursor.day,
                    "weekday": cursor.strftime("%A"),
                },
                "bikram_sambat": bs_struct(cursor),
            }
        )
        cursor = cursor.fromordinal(cursor.toordinal() + 1)
    month_confidence = get_bs_confidence(month_start)
    return {
        "year": year,
        "month": month,
        "month_label": month_start.strftime("%B %Y"),
        "supported_range": {
            "gregorian_min_year": min_year,
            "gregorian_max_year": max_year,
        },
        "days": rows,
        **_bs_support_meta(
            engine_path="dual_month_calendar_v3",
            confidence=month_confidence,
            uncertainty=build_bs_uncertainty(month_confidence, get_bs_estimated_error_days(month_start)),
            fallback_used=month_confidence == "estimated",
        ),
        "engine_version": "v3",
        "provenance": build_surface_provenance(
            calendar_context=_calendar_context(month_start, surface="dual_month")
        ),
        "policy": get_policy_metadata(),
    }


def build_bs_to_gregorian_payload(year: int, month: int, day: int) -> dict[str, Any]:
    gregorian_date = bs_to_gregorian(year, month, day)
    confidence = get_bs_year_confidence(year)
    estimated_error_days = "0-1" if confidence == "estimated" else None
    uncertainty = build_bs_uncertainty(confidence, estimated_error_days)
    return {
        "bs": {
            "year": year,
            "month": month,
            "day": day,
            "month_name": get_bs_month_name(month),
            "confidence": confidence,
            "source_range": f"{BS_MIN_YEAR}-{BS_MAX_YEAR}" if confidence == "official" else None,
            "estimated_error_days": estimated_error_days,
            "uncertainty": uncertainty,
        },
        "gregorian": gregorian_date.isoformat(),
        **_bs_support_meta(
            engine_path="bs_to_gregorian_v3",
            confidence=confidence,
            uncertainty=uncertainty,
            fallback_used=confidence == "estimated",
        ),
        "engine_version": "v3",
        "provenance": build_surface_provenance(
            calendar_context=_calendar_context(gregorian_date, surface="bs_to_gregorian")
        ),
        "policy": get_policy_metadata(),
    }
