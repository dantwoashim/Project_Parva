"""Shared builders for calendar-facing API payloads."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Optional

from fastapi import HTTPException

from app.cache import load_precomputed_festival_year, load_precomputed_panchanga
from app.calendar.bikram_sambat import (
    get_bs_confidence,
    get_bs_estimated_error_days,
    get_bs_month_name,
    get_bs_source_range,
    gregorian_to_bs,
)
from app.core.clock import DEFAULT_CIVIL_TIMEZONE, SYSTEM_CLOCK, Clock, civil_date
from app.core.source_metadata import (
    PUBLIC_FESTIVAL_RULES,
    build_bs_claim_meta,
    build_calculated_claim_meta,
)
from app.domain.temporal_context import CalendarContext, LocationContext
from app.policy import get_policy_metadata
from app.rules import get_rule_service
from app.services import calendar_conversion_service as conversion_service
from app.services.trust_surface_service import (
    build_portable_proof_capsule,
    build_surface_meta,
    build_surface_provenance,
    build_temporal_risk_payload,
)
from app.uncertainty import build_bs_uncertainty, build_panchanga_uncertainty


def build_provenance(
    *,
    festival_id: Optional[str] = None,
    year: Optional[int] = None,
    calendar_context: CalendarContext | None = None,
) -> dict[str, Any]:
    return build_surface_provenance(
        festival_id=festival_id,
        year=year,
        calendar_context=calendar_context,
        create_if_missing=True,
    )


def parse_iso_date(date_str: str) -> date:
    return conversion_service.parse_iso_date(date_str)


def _calendar_context(
    target_date: date,
    *,
    surface: str,
    risk_mode: str = "standard",
    support_tier: str | None = None,
    snapshot_id: str | None = None,
) -> CalendarContext:
    return CalendarContext(
        target_date=target_date,
        surface=surface,
        risk_mode=risk_mode,
        support_tier=support_tier,
        snapshot_id=snapshot_id,
    )


def _location_context(
    *,
    latitude: float | None = None,
    longitude: float | None = None,
    timezone_name: str | None = None,
    source: str = "runtime",
) -> LocationContext:
    return LocationContext(
        latitude=latitude,
        longitude=longitude,
        timezone_name=timezone_name,
        source=source,
    )


def _calendar_meta(
    *,
    engine_path: str,
    confidence: str,
    quality_band: str,
    uncertainty: dict[str, Any] | None = None,
    fallback_used: bool | None = None,
) -> dict[str, Any]:
    return build_surface_meta(
        engine_path=engine_path,
        confidence=confidence,
        quality_band=quality_band,
        uncertainty=uncertainty,
        fallback_used=fallback_used,
    )


def _bs_support_meta(
    *,
    engine_path: str,
    confidence: str,
    uncertainty: dict[str, Any] | None,
    fallback_used: bool = False,
) -> dict[str, Any]:
    quality_band = "validated" if confidence == "official" else "provisional"
    return _calendar_meta(
        engine_path=engine_path,
        confidence=confidence,
        quality_band=quality_band,
        uncertainty=uncertainty,
        fallback_used=fallback_used,
    )


def _calendar_risk_payload(
    *,
    progress: Any,
    fallback_used: bool,
    support_tier: str,
    method: str,
    risk_mode: str = "standard",
) -> dict[str, Any]:
    return build_temporal_risk_payload(
        progress=progress,
        support_tier=support_tier,
        fallback_used=fallback_used,
        method=method,
        risk_mode=risk_mode,
    )


def bs_struct(gregorian_date: date) -> dict[str, Any]:
    return conversion_service.bs_struct(gregorian_date)


def build_bs_date_payload(gregorian_date: date) -> dict[str, Any]:
    return conversion_service.build_bs_date_payload(gregorian_date)


def build_ns_date_payload(gregorian_date: date) -> Optional[dict[str, Any]]:
    return conversion_service.build_ns_date_payload(gregorian_date)


def build_tithi_payload(gregorian_date: date) -> dict[str, Any]:
    return conversion_service.build_tithi_payload(gregorian_date)


def build_conversion_payload(gregorian_date: date, *, trace_id: str | None = None) -> dict[str, Any]:
    return conversion_service.build_conversion_payload(gregorian_date, trace_id=trace_id)


def build_compare_conversion_payload(gregorian_date: date, *, trace_id: str | None = None) -> dict[str, Any]:
    return conversion_service.build_compare_conversion_payload(gregorian_date, trace_id=trace_id)


def build_today_payload(
    *,
    risk_mode: str = "standard",
    trace_id: str | None = None,
    today: date | None = None,
    clock: Clock = SYSTEM_CLOCK,
    timezone_name: str = DEFAULT_CIVIL_TIMEZONE,
) -> dict[str, Any]:
    today = today or civil_date(clock=clock, timezone_name=timezone_name)
    bs_payload = build_bs_date_payload(today)
    tithi_payload = build_tithi_payload(today)
    meta = _calendar_meta(
        engine_path=str(tithi_payload.get("method") or "calendar_today_v3"),
        confidence=str(tithi_payload.get("confidence") or "computed"),
        quality_band="validated",
        uncertainty=tithi_payload.get("uncertainty"),
    )
    risk = _calendar_risk_payload(
        progress=tithi_payload.get("progress"),
        fallback_used=bool(meta["fallback_used"]),
        support_tier=str(meta["support_tier"]),
        method=str(tithi_payload.get("method") or "calendar_today_v3"),
        risk_mode=risk_mode,
    )
    context = _calendar_context(
        today,
        surface="today",
        risk_mode=risk_mode,
        support_tier=str(meta["support_tier"]),
    )
    return {
        "gregorian": today.isoformat(),
        "bikram_sambat": bs_payload,
        "tithi": tithi_payload,
        **meta,
        **risk,
        "engine_version": "v3",
        "provenance": build_provenance(calendar_context=context),
        "policy": get_policy_metadata(),
        "meta": build_bs_claim_meta(
            int(bs_payload["year"]),
            trace_id=trace_id,
            result_class="today_calendar_context",
        ),
    }


def build_panchanga_payload(
    target_date: date,
    *,
    risk_mode: str = "standard",
    trace_id: str | None = None,
    latitude: float = 27.7172,
    longitude: float = 85.3240,
    timezone_name: str = "Asia/Kathmandu",
    ayanamsa: str = "lahiri",
) -> dict[str, Any]:
    from app.panchanga.ephemeris_provider import BuiltInApproxProvider

    default_context = (
        latitude == 27.7172
        and longitude == 85.3240
        and timezone_name == "Asia/Kathmandu"
        and ayanamsa == "lahiri"
    )
    cached_payload = load_precomputed_panchanga(target_date) if default_context else None
    if cached_payload:
        response = dict(cached_payload)
        response["date"] = target_date.isoformat()
        response["engine_version"] = "v2"
        response["policy"] = get_policy_metadata()
        response["service_status"] = (
            "degraded_cached" if response.get("cache", {}).get("stale") else "healthy"
        )
        response["cache"] = {
            "hit": True,
            "source": "precomputed",
        }
        response["observation_context"] = {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone_name,
            "ayanamsa": ayanamsa,
        }
        ephemeris = dict(response.get("ephemeris") or {})
        ephemeris.setdefault("mode", "swiss_moshier")
        ephemeris.setdefault("ayanamsa", ayanamsa)
        ephemeris.setdefault("coordinate_system", "sidereal")
        response["ephemeris"] = ephemeris
        meta = _calendar_meta(
            engine_path=str(
                (((response.get("panchanga") or {}).get("tithi") or {}).get("method"))
                or "ephemeris_udaya"
            ),
            confidence="computed",
            quality_band="provisional" if response["service_status"] == "degraded_cached" else "validated",
            uncertainty=(response.get("panchanga") or {}).get("uncertainty"),
            fallback_used=response["service_status"] == "degraded_cached",
        )
        risk = _calendar_risk_payload(
            progress=(((response.get("panchanga") or {}).get("tithi") or {}).get("progress")),
            fallback_used=bool(meta["fallback_used"]),
            support_tier=str(meta["support_tier"]),
            method=str((((response.get("panchanga") or {}).get("tithi") or {}).get("method")) or "ephemeris_udaya"),
            risk_mode=risk_mode,
        )
        response.update(meta)
        response.update(risk)
        response["provenance"] = build_provenance(
            calendar_context=_calendar_context(
                target_date,
                surface="panchanga",
                risk_mode=risk_mode,
                support_tier=str(meta["support_tier"]),
            )
        )
        response["meta"] = build_calculated_claim_meta(
            trace_id=trace_id,
            result_class="panchanga",
            warnings=["precomputed_panchanga_cache_used"],
        )
        return response

    try:
        panchanga = BuiltInApproxProvider().panchanga_for(
            target_date,
            latitude=latitude,
            longitude=longitude,
            timezone_name=timezone_name,
            ayanamsa=ayanamsa,
        )
    except (KeyError, TypeError, ValueError, RuntimeError) as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Panchanga engine unavailable and no precomputed artifact found for "
                f"{target_date.isoformat()}. Run precompute pipeline or retry."
            ),
        ) from exc

    bs_year, bs_month, bs_day = gregorian_to_bs(target_date)

    uncertainty = build_panchanga_uncertainty()
    meta = _calendar_meta(
        engine_path="ephemeris_udaya",
        confidence="computed",
        quality_band="validated",
        uncertainty=uncertainty,
    )
    risk = _calendar_risk_payload(
        progress=panchanga["tithi"]["progress"],
        fallback_used=bool(meta["fallback_used"]),
        support_tier=str(meta["support_tier"]),
        method="ephemeris_udaya",
        risk_mode=risk_mode,
    )
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
            "uncertainty": uncertainty,
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
            "ayanamsa": panchanga.get("ayanamsa", ayanamsa),
            "coordinate_system": panchanga.get("coordinate_system", "sidereal"),
        },
        "observation_context": {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone_name,
            "ayanamsa": panchanga.get("ayanamsa", ayanamsa),
        },
        "cache": {
            "hit": False,
            "source": "computed",
        },
        "service_status": "healthy",
        **meta,
        **risk,
        "engine_version": "v3",
        "provenance": build_provenance(
            calendar_context=_calendar_context(
                target_date,
                surface="panchanga",
                risk_mode=risk_mode,
                support_tier=str(meta["support_tier"]),
            )
        ),
        "policy": get_policy_metadata(),
        "meta": build_calculated_claim_meta(trace_id=trace_id, result_class="panchanga"),
    }


def build_panchanga_range_payload(start: date, days: int, *, trace_id: str | None = None) -> dict[str, Any]:
    from app.calendar.panchanga import get_panchanga

    results = []
    cache_hits = 0
    cache_misses = 0
    for offset in range(days):
        current = start + timedelta(days=offset)
        cached = load_precomputed_panchanga(current)
        if cached:
            results.append(
                {
                    "date": current.isoformat(),
                    "tithi": cached["panchanga"]["tithi"]["name"],
                    "nakshatra": cached["panchanga"]["nakshatra"]["name"],
                    "yoga": cached["panchanga"]["yoga"]["name"],
                    "vaara": cached["panchanga"]["vaara"]["name_english"],
                }
            )
            cache_hits += 1
            continue

        panchanga = get_panchanga(current)
        results.append(
            {
                "date": panchanga["date"].isoformat()
                if hasattr(panchanga["date"], "isoformat")
                else str(panchanga["date"]),
                "tithi": panchanga["tithi"]["name"],
                "nakshatra": panchanga["nakshatra"]["name"],
                "yoga": panchanga["yoga"]["name"],
                "vaara": panchanga["vaara"]["name_english"],
            }
        )
        cache_misses += 1

    if cache_hits and cache_misses:
        engine_path = "panchanga_range_mixed"
    elif cache_hits:
        engine_path = "precomputed_panchanga_range"
    else:
        engine_path = "ephemeris_panchanga_range"

    return {
        "start": start.isoformat(),
        "days": days,
        "panchangas": results,
        "cache": {
            "hits": cache_hits,
            "misses": cache_misses,
            "hit_ratio": round(cache_hits / days, 4) if days else 0.0,
        },
        **_calendar_meta(
            engine_path=engine_path,
            confidence="computed",
            quality_band="provisional" if cache_misses else "validated",
            fallback_used=False,
        ),
        "engine_version": "v3",
        "provenance": build_provenance(
            calendar_context=_calendar_context(start, surface="panchanga_range")
        ),
        "policy": get_policy_metadata(),
        "meta": build_calculated_claim_meta(
            trace_id=trace_id,
            result_class="panchanga_range",
            warnings=["range_payload_summarizes_multiple_daily_calculations"],
        ),
    }


def build_dual_month_payload(year: int, month: int, *, trace_id: str | None = None) -> dict[str, Any]:
    return conversion_service.build_dual_month_payload(year, month, trace_id=trace_id)


def build_bs_to_gregorian_payload(
    year: int,
    month: int,
    day: int,
    *,
    trace_id: str | None = None,
) -> dict[str, Any]:
    return conversion_service.build_bs_to_gregorian_payload(year, month, day, trace_id=trace_id)


def build_tithi_detail_payload(
    target_date: date,
    *,
    latitude: float,
    longitude: float,
    risk_mode: str = "standard",
    trace_id: str | None = None,
) -> dict[str, Any]:
    from app.calendar.tithi import calculate_tithi, get_moon_phase_name, get_udaya_tithi
    from app.calendar.tithi.tithi_udaya import detect_ksheepana, detect_vriddhi
    from app.uncertainty import build_tithi_uncertainty

    try:
        udaya = get_udaya_tithi(target_date, latitude=latitude, longitude=longitude)
        sunrise_npt = udaya["sunrise_local"]
        tithi_payload = {
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
        }
    except (KeyError, TypeError, ValueError, RuntimeError):
        tithi_data = calculate_tithi(target_date)
        tithi_payload = {
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
        }

    meta = _calendar_meta(
        engine_path=str(tithi_payload.get("method") or "tithi_v3"),
        confidence=str(tithi_payload.get("confidence") or "computed"),
        quality_band="validated"
        if tithi_payload.get("method") == "ephemeris_udaya"
        else "provisional",
        uncertainty=tithi_payload.get("uncertainty"),
    )
    risk = _calendar_risk_payload(
        progress=tithi_payload.get("progress"),
        fallback_used=bool(meta["fallback_used"]),
        support_tier=str(meta["support_tier"]),
        method=str(tithi_payload.get("method") or "tithi_v3"),
        risk_mode=risk_mode,
    )

    return {
        "date": target_date.isoformat(),
        "location": {"latitude": latitude, "longitude": longitude},
        "location_context": _location_context(
            latitude=latitude,
            longitude=longitude,
            source="query",
        ).as_dict(),
        "tithi": tithi_payload,
        **meta,
        **risk,
        "engine_version": "v3",
        "provenance": build_provenance(
            calendar_context=_calendar_context(
                target_date,
                surface="tithi",
                risk_mode=risk_mode,
                support_tier=str(meta["support_tier"]),
            )
        ),
        "policy": get_policy_metadata(),
        "meta": build_calculated_claim_meta(trace_id=trace_id, result_class="tithi"),
    }


def build_upcoming_festivals_payload(
    days: int,
    *,
    today: Optional[date] = None,
    trace_id: str | None = None,
    clock: Clock = SYSTEM_CLOCK,
    timezone_name: str = DEFAULT_CIVIL_TIMEZONE,
) -> dict[str, Any]:
    today = today or civil_date(clock=clock, timezone_name=timezone_name)
    end_date = today + timedelta(days=days)
    rule_service = get_rule_service()
    upcoming: list[dict[str, Any]] = []
    cache_years_loaded: list[int] = []

    for year in [today.year, today.year + 1]:
        payload = load_precomputed_festival_year(year)
        if not payload or not isinstance(payload.get("festivals"), list):
            continue
        cache_years_loaded.append(year)
        for row in payload["festivals"]:
            try:
                start_dt = date.fromisoformat(str(row["start"]))
                end_dt = date.fromisoformat(str(row["end"]))
            except (TypeError, ValueError):
                continue
            if start_dt < today or start_dt > end_date:
                continue
            upcoming.append(
                {
                    "festival_id": row["festival_id"],
                    "start": start_dt.isoformat(),
                    "end": end_dt.isoformat(),
                    "days_until": (start_dt - today).days,
                }
            )

    if cache_years_loaded:
        upcoming.sort(key=lambda item: item["start"])
        return {
            "from_date": today.isoformat(),
            "days": days,
            "festivals": upcoming,
            "cache": {
                "hit": True,
                "years_loaded": sorted(set(cache_years_loaded)),
                "source": "precomputed",
            },
            **_calendar_meta(
                engine_path="precomputed_festival_slice",
                confidence="computed",
                quality_band="validated",
                fallback_used=False,
            ),
            "engine_version": "v3",
            "provenance": build_provenance(
                calendar_context=_calendar_context(today, surface="upcoming_festivals")
            ),
            "policy": get_policy_metadata(),
            "meta": build_calculated_claim_meta(
                trace_id=trace_id,
                result_class="upcoming_festivals",
                source=PUBLIC_FESTIVAL_RULES,
                warnings=["precomputed_festival_cache_used"],
            ),
        }

    for festival_id in rule_service.list_ids():
        result = rule_service.calculate(festival_id, today.year)
        if result and today <= result.start_date <= end_date:
            upcoming.append(
                {
                    "festival_id": festival_id,
                    "start": result.start_date.isoformat(),
                    "end": result.end_date.isoformat(),
                    "days_until": (result.start_date - today).days,
                }
            )
        elif result and result.start_date < today:
            result_next = rule_service.calculate(festival_id, today.year + 1)
            if result_next and result_next.start_date <= end_date:
                upcoming.append(
                    {
                        "festival_id": festival_id,
                        "start": result_next.start_date.isoformat(),
                        "end": result_next.end_date.isoformat(),
                        "days_until": (result_next.start_date - today).days,
                    }
                )

    upcoming.sort(key=lambda item: item["start"])
    return {
        "from_date": today.isoformat(),
        "days": days,
        "festivals": upcoming,
        "cache": {
            "hit": False,
            "years_loaded": [],
            "source": "computed",
        },
        **_calendar_meta(
            engine_path="festival_rule_service_upcoming",
            confidence="computed",
            quality_band="provisional",
            fallback_used=False,
        ),
        "engine_version": "v3",
        "provenance": build_provenance(
            calendar_context=_calendar_context(today, surface="upcoming_festivals")
        ),
        "policy": get_policy_metadata(),
        "meta": build_calculated_claim_meta(
            trace_id=trace_id,
            result_class="upcoming_festivals",
            source=PUBLIC_FESTIVAL_RULES,
        ),
    }


def build_calendar_proof_capsule(
    *,
    surface: str,
    payload: dict[str, Any],
    request: dict[str, Any],
) -> dict[str, Any]:
    target_date = payload.get("date") or payload.get("gregorian")
    calendar_context = None
    if isinstance(target_date, str):
        try:
            calendar_context = _calendar_context(
                date.fromisoformat(target_date),
                surface=surface,
                risk_mode=str(payload.get("risk_mode") or "standard"),
                support_tier=str(payload.get("support_tier") or ""),
                snapshot_id=((payload.get("provenance") or {}).get("snapshot_id")),
            )
        except ValueError:
            calendar_context = None

    location_context = None
    location_payload = payload.get("location_context") or payload.get("location")
    if isinstance(location_payload, dict):
        location_context = _location_context(
            latitude=location_payload.get("latitude"),
            longitude=location_payload.get("longitude"),
            timezone_name=location_payload.get("timezone"),
            source=location_payload.get("source", "runtime"),
        )

    return build_portable_proof_capsule(
        surface=surface,
        payload=payload,
        request=request,
        calendar_context=calendar_context,
        location_context=location_context,
    )
