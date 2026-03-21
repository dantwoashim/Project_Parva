"""Application services for personal panchanga and context responses."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from app.calendar.bikram_sambat import (
    get_bs_confidence,
    get_bs_estimated_error_days,
    get_bs_month_name,
    get_bs_source_range,
    gregorian_to_bs,
)
from app.calendar.panchanga import get_panchanga
from app.core.request_context import (
    CoordinateInput,
    DegradedState,
    base_meta_payload,
    build_input_degraded_state,
    normalize_coordinates,
    normalize_timezone,
    parse_date,
)
from app.explainability import create_reason_trace
from app.festivals.repository import get_repository
from app.rules import get_rule_service
from app.uncertainty import build_bs_uncertainty, build_panchanga_uncertainty


@dataclass(frozen=True)
class PersonalRequestContext:
    target_date: date
    latitude: float
    longitude: float
    timezone_name: str
    coord_warnings: tuple[str, ...]
    tz_warnings: tuple[str, ...]
    degraded: DegradedState

    @property
    def location_sources(self) -> dict[str, str]:
        return {
            "latitude": "default_kathmandu"
            if "latitude" in self.degraded.defaults_applied
            else "user_input",
            "longitude": "default_kathmandu"
            if "longitude" in self.degraded.defaults_applied
            else "user_input",
            "timezone": "default_kathmandu"
            if "timezone" in self.degraded.defaults_applied
            else "user_input",
        }

    @property
    def warnings(self) -> list[str]:
        return [*self.coord_warnings, *self.tz_warnings]


def _resolve_personal_request_context(
    *,
    date_str: str,
    lat: CoordinateInput,
    lon: CoordinateInput,
    tz: Optional[str],
) -> PersonalRequestContext:
    target_date = parse_date(date_str)
    latitude, longitude, coord_warnings = normalize_coordinates(lat, lon)
    timezone_name, tz_warnings = normalize_timezone(tz)
    degraded = build_input_degraded_state(
        lat_raw=lat,
        lon_raw=lon,
        tz_raw=tz,
        tz_warnings=tz_warnings,
    )
    return PersonalRequestContext(
        target_date=target_date,
        latitude=latitude,
        longitude=longitude,
        timezone_name=timezone_name,
        coord_warnings=tuple(coord_warnings),
        tz_warnings=tuple(tz_warnings),
        degraded=degraded,
    )


def _format_local_time(value: str | dict | None, fallback: str = "Time pending") -> str:
    if not value:
        return fallback
    if isinstance(value, dict):
        value = value.get("local") or value.get("utc") or value.get("local_time")
    if not value:
        return fallback
    if isinstance(value, str) and "T" not in value:
        parsed = datetime.strptime(value, "%H:%M:%S")
        return parsed.strftime("%I:%M %p").lstrip("0")
    parsed = datetime.fromisoformat(value)
    return parsed.strftime("%I:%M %p").lstrip("0")


def _context_title_for_payload(panchanga: dict) -> str:
    nakshatra = (panchanga.get("nakshatra") or {}).get("name", "").lower()
    if "rohini" in nakshatra or "shravan" in nakshatra:
        return "Morning Calm"
    if "swati" in nakshatra or "chitra" in nakshatra:
        return "Focused Momentum"
    return "Quiet Sanctuary"


def _context_summary_for_payload(panchanga: dict, timezone_name: str) -> str:
    tithi = (panchanga.get("tithi") or {}).get("name") or "Today"
    nakshatra = (panchanga.get("nakshatra") or {}).get("name") or "the current sky"
    sunrise = _format_local_time(panchanga.get("sunrise"), "Sunrise pending")
    return (
        f"{tithi} with {nakshatra} supports a steadier rhythm here. "
        f"Sunrise arrives around {sunrise} in {timezone_name}, favoring a calm start and deliberate plans."
    )


def _daily_inspiration_for_payload(panchanga: dict) -> str:
    tithi = (panchanga.get("tithi") or {}).get("name") or "the day"
    vaara = (panchanga.get("vaara") or {}).get("name_english") or "today"
    return f"The soul sits here, in the quiet spaces we keep. Let {tithi} guide the shape of {vaara.lower()}."


def _upcoming_reminders(target_date: date, limit: int = 2) -> list[dict]:
    repo = get_repository()
    upcoming = get_rule_service().upcoming(target_date, days=180)
    items: list[dict] = []
    for festival_id, dates in upcoming:
        festival = repo.get_by_id(festival_id)
        if not festival:
            continue
        items.append(
            {
                "id": festival.id,
                "title": festival.name,
                "date_label": dates.start_date.strftime("%b %d"),
                "status": "Upcoming",
            }
        )
        if len(items) >= limit:
            break
    return items


def build_personal_panchanga_response(
    *,
    date_str: str,
    lat: CoordinateInput,
    lon: CoordinateInput,
    tz: Optional[str],
) -> dict:
    context = _resolve_personal_request_context(date_str=date_str, lat=lat, lon=lon, tz=tz)
    panchanga = get_panchanga(
        context.target_date,
        latitude=context.latitude,
        longitude=context.longitude,
    )
    bs_year, bs_month, bs_day = gregorian_to_bs(context.target_date)
    timezone_source = context.location_sources["timezone"]

    payload = {
        "date": context.target_date.isoformat(),
        "location": {
            "latitude": context.latitude,
            "longitude": context.longitude,
            "timezone": context.timezone_name,
            "input_sources": context.location_sources,
        },
        "bikram_sambat": {
            "year": bs_year,
            "month": bs_month,
            "day": bs_day,
            "month_name": get_bs_month_name(bs_month),
            "confidence": get_bs_confidence(context.target_date),
            "source_range": get_bs_source_range(context.target_date),
            "estimated_error_days": get_bs_estimated_error_days(context.target_date),
            "uncertainty": build_bs_uncertainty(
                get_bs_confidence(context.target_date),
                get_bs_estimated_error_days(context.target_date),
            ),
        },
        "tithi": {
            "number": panchanga["tithi"]["display_number"],
            "absolute": panchanga["tithi"]["number"],
            "name": panchanga["tithi"]["name"],
            "paksha": panchanga["tithi"]["paksha"],
            "progress": panchanga["tithi"]["progress"],
            "method": "ephemeris_udaya",
        },
        "nakshatra": panchanga["nakshatra"],
        "yoga": panchanga["yoga"],
        "karana": panchanga["karana"],
        "vaara": panchanga["vaara"],
        "sunrise": panchanga["sunrise"],
        "local_sunrise": panchanga.get("sunrise"),
        "sunset": panchanga.get("sunset"),
        "local_sunset": panchanga.get("sunset"),
        "timezone_source": timezone_source,
        "ephemeris": {
            "mode": panchanga.get("mode", "swiss_moshier"),
            "accuracy": panchanga.get("accuracy", "arcsecond"),
            "library": panchanga.get("library", "pyswisseph"),
        },
        "uncertainty": build_panchanga_uncertainty(),
        "warnings": context.warnings,
    }

    trace = create_reason_trace(
        trace_type="personal_panchanga",
        subject={"date": context.target_date.isoformat()},
        inputs={
            "date": context.target_date.isoformat(),
            "lat": context.latitude,
            "lon": context.longitude,
            "tz": context.timezone_name,
        },
        outputs={
            "bs": f"{bs_year}-{bs_month}-{bs_day}",
            "tithi": payload["tithi"]["name"],
            "nakshatra": payload["nakshatra"]["name"],
            "vaara": payload["vaara"]["name_english"],
        },
        steps=[
            {"step": "sunrise", "detail": "Calculated sunrise at provided coordinates."},
            {
                "step": "panchanga",
                "detail": "Derived tithi/nakshatra/yoga/karana/vaara from ephemeris.",
            },
            {"step": "bs_conversion", "detail": "Converted Gregorian date to Bikram Sambat."},
        ],
    )

    return {
        **payload,
        **base_meta_payload(
            trace_id=trace["trace_id"],
            confidence="computed",
            method="ephemeris_udaya",
            method_profile="personal_panchanga_v2_udaya",
            quality_band="provisional" if context.degraded.active else "gold",
            assumption_set_id="np-personal-panchanga-v2",
            advisory_scope="ritual_planning",
            degraded=context.degraded,
        ),
    }


def build_personal_context_response(
    *,
    date_str: str,
    lat: CoordinateInput,
    lon: CoordinateInput,
    tz: Optional[str],
) -> dict:
    context = _resolve_personal_request_context(date_str=date_str, lat=lat, lon=lon, tz=tz)
    panchanga = get_panchanga(
        context.target_date,
        latitude=context.latitude,
        longitude=context.longitude,
    )

    payload = {
        "date": context.target_date.isoformat(),
        "location": {
            "latitude": context.latitude,
            "longitude": context.longitude,
            "timezone": context.timezone_name,
            "input_sources": context.location_sources,
        },
        "place_title": "Your sanctuary",
        "status_line": f"Sunrise {_format_local_time(panchanga.get('sunrise'))} - {context.timezone_name}",
        "visit_note": "Place-aware daily guidance stays synced to this location and date.",
        "context_title": _context_title_for_payload(panchanga),
        "context_summary": _context_summary_for_payload(panchanga, context.timezone_name),
        "temperature_note": None,
        "daily_inspiration": _daily_inspiration_for_payload(panchanga),
        "upcoming_reminders": _upcoming_reminders(context.target_date),
        "warnings": context.warnings,
    }

    trace = create_reason_trace(
        trace_type="personal_context",
        subject={"date": context.target_date.isoformat()},
        inputs={
            "date": context.target_date.isoformat(),
            "lat": context.latitude,
            "lon": context.longitude,
            "tz": context.timezone_name,
        },
        outputs={
            "context_title": payload["context_title"],
            "upcoming_reminders": len(payload["upcoming_reminders"]),
        },
        steps=[
            {
                "step": "panchanga",
                "detail": "Derived the place-aware daily context from the current panchanga signal set.",
            },
            {
                "step": "copy",
                "detail": "Synthesized sanctuary, context, and inspiration copy for the desktop My Place surface.",
            },
            {
                "step": "upcoming",
                "detail": "Attached the next upcoming observances for reminder enrichment.",
            },
        ],
    )

    return {
        **payload,
        **base_meta_payload(
            trace_id=trace["trace_id"],
            confidence="computed",
            method="personal_context_synthesis",
            method_profile="personal_context_v1",
            quality_band="provisional" if context.degraded.active else "gold",
            assumption_set_id="np-my-place-desktop-v1",
            advisory_scope="personal_guidance",
            degraded=context.degraded,
        ),
    }


__all__ = [
    "build_personal_context_response",
    "build_personal_panchanga_response",
]
