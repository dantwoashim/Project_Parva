"""Shared builders for calendar-facing API payloads."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Optional

from fastapi import HTTPException

from app.cache import load_precomputed_festival_year, load_precomputed_panchanga
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
from app.core.request_context import derive_support_tier
from app.festivals.risk_service import truth_ladder
from app.policy import get_policy_metadata
from app.provenance import get_latest_snapshot_id, get_provenance_payload
from app.uncertainty import build_bs_uncertainty, build_panchanga_uncertainty


def build_provenance(*, festival_id: Optional[str] = None, year: Optional[int] = None) -> dict[str, Any]:
    snapshot_id = get_latest_snapshot_id()
    verify_url = "/v3/api/provenance/root"
    if festival_id and year and snapshot_id:
        verify_url = (
            f"/v3/api/provenance/proof?festival={festival_id}&year={year}&snapshot={snapshot_id}"
        )
    return get_provenance_payload(verify_url=verify_url, create_if_missing=True)


def parse_iso_date(date_str: str) -> date:
    try:
        parts = date_str.split("-")
        return date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError) as exc:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD") from exc


def _fallback_used(method: str) -> bool:
    normalized = str(method or "").strip().lower()
    return "fallback" in normalized or "legacy" in normalized or "instantaneous" in normalized


def _calibration_status_from_uncertainty(uncertainty: dict[str, Any] | None) -> str:
    if not isinstance(uncertainty, dict):
        return "unavailable"
    mode = str(uncertainty.get("calibration_mode") or "unavailable").strip().lower()
    return "empirical" if mode == "empirical" else "unavailable"


def _calendar_meta(
    *,
    engine_path: str,
    confidence: str,
    quality_band: str,
    uncertainty: dict[str, Any] | None = None,
    fallback_used: bool | None = None,
) -> dict[str, Any]:
    return {
        "support_tier": derive_support_tier(
            confidence=confidence,
            quality_band=quality_band,
        ),
        "engine_path": engine_path,
        "fallback_used": _fallback_used(engine_path) if fallback_used is None else fallback_used,
        "calibration_status": _calibration_status_from_uncertainty(uncertainty),
    }


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


def _normalize_progress(progress: Any) -> float | None:
    try:
        value = float(progress)
    except (TypeError, ValueError):
        return None
    if 0.0 <= value <= 1.0:
        return value
    if 0.0 <= value <= 100.0:
        return value / 100.0
    return None


def _calendar_boundary_radar(
    *,
    progress: Any,
    fallback_used: bool,
    support_tier: str,
    method: str,
) -> str:
    normalized_method = str(method or "").strip().lower()
    normalized_tier = str(support_tier or "").strip().lower()
    progress_value = _normalize_progress(progress)

    if progress_value is not None:
        distance = min(progress_value, 1.0 - progress_value)
        if distance <= 0.08:
            return "high_disagreement_risk"
        if distance <= 0.18:
            return "one_day_sensitive"

    if normalized_method == "instantaneous":
        return "one_day_sensitive"
    if fallback_used or normalized_tier in {"heuristic", "estimated", "conflicted"}:
        return "one_day_sensitive"
    return "stable"


def _calendar_stability_score(
    *,
    progress: Any,
    fallback_used: bool,
    support_tier: str,
    method: str,
) -> float:
    normalized_method = str(method or "").strip().lower()
    normalized_tier = str(support_tier or "").strip().lower()
    progress_value = _normalize_progress(progress)

    score = {
        "authoritative": 0.97,
        "computed": 0.86,
        "heuristic": 0.62,
        "estimated": 0.5,
        "conflicted": 0.48,
    }.get(normalized_tier, 0.7)

    if normalized_method == "instantaneous":
        score -= 0.12
    if fallback_used:
        score -= 0.1
    if progress_value is not None:
        distance = min(progress_value, 1.0 - progress_value)
        if distance <= 0.08:
            score -= 0.28
        elif distance <= 0.18:
            score -= 0.14

    return round(min(max(score, 0.05), 0.99), 2)


def _calendar_risk_payload(
    *,
    progress: Any,
    fallback_used: bool,
    support_tier: str,
    method: str,
    risk_mode: str = "standard",
) -> dict[str, Any]:
    boundary_radar = _calendar_boundary_radar(
        progress=progress,
        fallback_used=fallback_used,
        support_tier=support_tier,
        method=method,
    )
    stability_score = _calendar_stability_score(
        progress=progress,
        fallback_used=fallback_used,
        support_tier=support_tier,
        method=method,
    )
    normalized_mode = str(risk_mode or "standard").strip().lower()
    abstained = normalized_mode == "strict" and boundary_radar == "high_disagreement_risk"

    if abstained:
        recommended_action = (
            "Strict mode withheld a single-answer promotion because this calculation sits close to a boundary."
        )
    elif boundary_radar == "one_day_sensitive":
        recommended_action = (
            "Inspect method, provenance, and nearby boundary conditions before using this result operationally."
        )
    else:
        recommended_action = "This result is stable enough for normal consumer use."

    return {
        "risk_mode": normalized_mode,
        "boundary_radar": boundary_radar,
        "stability_score": stability_score,
        "abstained": abstained,
        "recommended_action": recommended_action,
    }


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
    uncertainty = tithi_payload.get("uncertainty")
    return {
        "gregorian": gregorian_date.isoformat(),
        "bikram_sambat": bs_payload,
        "nepal_sambat": build_ns_date_payload(gregorian_date),
        "tithi": tithi_payload,
        **_calendar_meta(
            engine_path=str(tithi_payload.get("method") or "calendar_conversion_v3"),
            confidence="estimated"
            if bs_payload.get("confidence") == "estimated"
            else str(tithi_payload.get("confidence") or "computed"),
            quality_band="validated",
            uncertainty=uncertainty,
        ),
        "engine_version": "v3",
        "provenance": build_provenance(),
        "policy": get_policy_metadata(),
    }


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
        **_calendar_meta(
            engine_path="bs_compare_official_vs_estimated",
            confidence="estimated" if official is None or match is False else "computed",
            quality_band="validated",
            uncertainty=(estimated or {}).get("uncertainty"),
            fallback_used=official is None,
        ),
        "engine_version": "v3",
        "provenance": build_provenance(),
        "policy": get_policy_metadata(),
    }


def build_today_payload(*, risk_mode: str = "standard") -> dict[str, Any]:
    today = date.today()
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
    return {
        "gregorian": today.isoformat(),
        "bikram_sambat": bs_payload,
        "tithi": tithi_payload,
        **meta,
        **risk,
        "engine_version": "v3",
        "provenance": build_provenance(),
        "policy": get_policy_metadata(),
    }


def build_panchanga_payload(target_date: date, *, risk_mode: str = "standard") -> dict[str, Any]:
    from app.calendar.panchanga import get_panchanga

    cached_payload = load_precomputed_panchanga(target_date)
    if cached_payload:
        response = dict(cached_payload)
        response["date"] = target_date.isoformat()
        response["engine_version"] = "v2"
        response["provenance"] = build_provenance()
        response["policy"] = get_policy_metadata()
        response["service_status"] = (
            "degraded_cached" if response.get("cache", {}).get("stale") else "healthy"
        )
        response["cache"] = {
            "hit": True,
            "source": "precomputed",
        }
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
        return response

    try:
        panchanga = get_panchanga(target_date)
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
        },
        "cache": {
            "hit": False,
            "source": "computed",
        },
        "service_status": "healthy",
        **meta,
        **risk,
        "engine_version": "v3",
        "provenance": build_provenance(),
        "policy": get_policy_metadata(),
    }


def build_panchanga_range_payload(start: date, days: int) -> dict[str, Any]:
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
        "provenance": build_provenance(),
        "policy": get_policy_metadata(),
    }


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
        cursor += timedelta(days=1)

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
            uncertainty=build_bs_uncertainty(
                month_confidence,
                get_bs_estimated_error_days(month_start),
            ),
            fallback_used=month_confidence == "estimated",
        ),
        "engine_version": "v3",
        "provenance": build_provenance(),
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
        "provenance": build_provenance(),
        "policy": get_policy_metadata(),
    }


def build_tithi_detail_payload(
    target_date: date,
    *,
    latitude: float,
    longitude: float,
    risk_mode: str = "standard",
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
        "tithi": tithi_payload,
        **meta,
        **risk,
        "engine_version": "v3",
        "provenance": build_provenance(),
        "policy": get_policy_metadata(),
    }


def build_upcoming_festivals_payload(days: int, *, today: Optional[date] = None) -> dict[str, Any]:
    from app.calendar.calculator_v2 import calculate_festival_v2, list_festivals_v2

    today = today or date.today()
    end_date = today + timedelta(days=days)
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
            "provenance": build_provenance(),
            "policy": get_policy_metadata(),
        }

    for festival_id in list_festivals_v2():
        result = calculate_festival_v2(festival_id, today.year)
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
            result_next = calculate_festival_v2(festival_id, today.year + 1)
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
            engine_path="calculator_v2_upcoming",
            confidence="computed",
            quality_band="provisional",
            fallback_used=False,
        ),
        "engine_version": "v3",
        "provenance": build_provenance(),
        "policy": get_policy_metadata(),
    }


def build_calendar_proof_capsule(
    *,
    surface: str,
    payload: dict[str, Any],
    request: dict[str, Any],
) -> dict[str, Any]:
    tithi = payload.get("tithi") or ((payload.get("panchanga") or {}).get("tithi") or {})
    return {
        "surface": surface,
        "request": request,
        "selection": {
            "date": payload.get("date") or payload.get("gregorian"),
            "support_tier": payload.get("support_tier"),
            "engine_path": payload.get("engine_path"),
            "fallback_used": payload.get("fallback_used"),
            "calibration_status": payload.get("calibration_status"),
            "abstained": payload.get("abstained", False),
        },
        "source_lineage": {
            "method": payload.get("method") or tithi.get("method"),
            "confidence": payload.get("confidence") or tithi.get("confidence"),
            "reference_time": tithi.get("reference_time"),
            "sunrise_used": tithi.get("sunrise_used"),
            "service_status": payload.get("service_status"),
            "cache": payload.get("cache"),
        },
        "risk": {
            "boundary_radar": payload.get("boundary_radar"),
            "stability_score": payload.get("stability_score"),
            "risk_mode": payload.get("risk_mode"),
            "recommended_action": payload.get("recommended_action"),
            "truth_ladder": truth_ladder(),
        },
        "provenance": payload.get("provenance"),
        "policy": payload.get("policy"),
        "calculation_trace_id": payload.get("calculation_trace_id"),
    }
