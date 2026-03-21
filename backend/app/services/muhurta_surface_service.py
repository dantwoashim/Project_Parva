"""Application services for muhurta response assembly."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

from app.calendar.muhurta import get_auspicious_windows, get_muhurtas, get_rahu_kalam
from app.core.request_context import (
    CoordinateInput,
    base_meta_payload,
    normalize_coordinates,
    normalize_timezone,
    parse_date,
)
from app.explainability import create_reason_trace


@dataclass(frozen=True)
class MuhurtaRequestContext:
    target_date: date
    latitude: float
    longitude: float
    timezone_name: str
    warnings: tuple[str, ...]


def _resolve_muhurta_request_context(
    *,
    date_str: str,
    lat: CoordinateInput,
    lon: CoordinateInput,
    tz: Optional[str],
) -> MuhurtaRequestContext:
    target_date = parse_date(date_str)
    latitude, longitude, coord_warnings = normalize_coordinates(lat, lon)
    timezone_name, tz_warnings = normalize_timezone(tz)
    return MuhurtaRequestContext(
        target_date=target_date,
        latitude=latitude,
        longitude=longitude,
        timezone_name=timezone_name,
        warnings=tuple([*coord_warnings, *tz_warnings]),
    )


def _window_reason_codes(row: dict) -> list[str]:
    codes: list[str] = []
    if row.get("quality"):
        codes.append(f"quality:{row['quality']}")

    hora = row.get("hora") or {}
    if hora.get("lord"):
        codes.append(f"hora:{hora['lord']}")

    chaughadia = row.get("chaughadia") or {}
    if chaughadia.get("name"):
        codes.append(f"chaughadia:{chaughadia['name']}")

    if row.get("is_abhijit"):
        codes.append("window:abhijit")
    if row.get("overlaps_avoidance"):
        codes.append("window:avoidance_overlap")

    breakdown = row.get("score_breakdown") or {}
    for key, value in breakdown.items():
        if not isinstance(value, (int, float)) or value == 0:
            continue
        if value > 0:
            codes.append(f"boost:{key}")
        else:
            codes.append(f"penalty:{key}")
    return codes


def _confidence_score(score: float | int | None) -> float:
    if score is None:
        return 0.0
    try:
        normalized = (float(score) + 100.0) / 200.0
    except (TypeError, ValueError):
        return 0.0
    return round(max(0.0, min(1.0, normalized)), 3)


def _rank_explanation(row: dict) -> str:
    breakdown = row.get("score_breakdown") or {}
    contributions: list[str] = []

    positives = sorted(
        [(k, v) for k, v in breakdown.items() if isinstance(v, (int, float)) and v > 0],
        key=lambda item: abs(item[1]),
        reverse=True,
    )
    negatives = sorted(
        [(k, v) for k, v in breakdown.items() if isinstance(v, (int, float)) and v < 0],
        key=lambda item: abs(item[1]),
        reverse=True,
    )

    if positives:
        top = ", ".join(f"{k} (+{int(v)})" for k, v in positives[:2])
        contributions.append(f"Boosted by {top}")

    if negatives:
        top = ", ".join(f"{k} ({int(v)})" for k, v in negatives[:2])
        contributions.append(f"Penalized by {top}")

    if row.get("overlaps_avoidance"):
        contributions.append("overlaps with avoidance window")

    if not contributions:
        contributions.append("base-quality ranking")

    return "; ".join(contributions)


def _enrich_ranked_window(row: dict) -> dict:
    enriched = dict(row)
    score = row.get("score")
    enriched["reason_codes"] = _window_reason_codes(row)
    enriched["rank_explanation"] = _rank_explanation(row)
    enriched["confidence_score"] = _confidence_score(score)
    return enriched


def build_muhurta_for_day_response(
    *,
    date_str: str,
    lat: CoordinateInput,
    lon: CoordinateInput,
    tz: Optional[str],
    birth_nakshatra: Optional[str],
) -> dict:
    context = _resolve_muhurta_request_context(date_str=date_str, lat=lat, lon=lon, tz=tz)
    muhurta = get_muhurtas(
        context.target_date,
        lat=context.latitude,
        lon=context.longitude,
        tz_name=context.timezone_name,
        birth_nakshatra=birth_nakshatra,
    )

    trace = create_reason_trace(
        trace_type="muhurta_daily",
        subject={"date": context.target_date.isoformat()},
        inputs={
            "date": context.target_date.isoformat(),
            "lat": context.latitude,
            "lon": context.longitude,
            "tz": context.timezone_name,
            "birth_nakshatra": birth_nakshatra,
        },
        outputs={
            "total_muhurtas": muhurta["total_muhurtas"],
            "abhijit_muhurta": muhurta["abhijit_muhurta"]["name"],
            "daylight_minutes": muhurta["daylight_minutes"],
            "night_minutes": muhurta["night_minutes"],
        },
        steps=[
            {
                "step": "solar_windows",
                "detail": "Computed sunrise/sunset/next sunrise for location and timezone.",
            },
            {
                "step": "day_night_muhurta",
                "detail": "Split day and night into 15 muhurtas each (30 total).",
            },
            {
                "step": "hora_chaughadia",
                "detail": "Attached hora lords and day/night chaughadia windows.",
            },
            {
                "step": "tara_bala",
                "detail": "Computed tara-bala profile when birth nakshatra is provided.",
            },
        ],
    )

    return {
        "date": context.target_date.isoformat(),
        "location": {
            "latitude": context.latitude,
            "longitude": context.longitude,
            "timezone": context.timezone_name,
        },
        "muhurtas": muhurta["muhurtas"],
        "day_muhurtas": muhurta["day_muhurtas"],
        "night_muhurtas": muhurta["night_muhurtas"],
        "abhijit_muhurta": muhurta["abhijit_muhurta"],
        "sunrise": muhurta["sunrise"],
        "sunset": muhurta["sunset"],
        "next_sunrise": muhurta["next_sunrise"],
        "daylight_minutes": muhurta["daylight_minutes"],
        "night_minutes": muhurta["night_minutes"],
        "hora": muhurta["hora"],
        "chaughadia": muhurta["chaughadia"],
        "tara_bala": muhurta["tara_bala"],
        "warnings": list(context.warnings),
        **base_meta_payload(
            trace_id=trace["trace_id"],
            confidence="computed",
            method="muhurta_day_night_partition",
            method_profile="muhurta_v2_hora_chaughadia_tarabala",
            quality_band="validated",
            assumption_set_id="np-mainstream-v2",
            advisory_scope="ritual_planning",
        ),
    }


def build_rahu_kalam_response(
    *,
    date_str: str,
    lat: CoordinateInput,
    lon: CoordinateInput,
    tz: Optional[str],
) -> dict:
    context = _resolve_muhurta_request_context(date_str=date_str, lat=lat, lon=lon, tz=tz)
    kalam = get_rahu_kalam(
        context.target_date,
        lat=context.latitude,
        lon=context.longitude,
        tz_name=context.timezone_name,
    )

    trace = create_reason_trace(
        trace_type="rahu_kalam",
        subject={"date": context.target_date.isoformat()},
        inputs={
            "date": context.target_date.isoformat(),
            "lat": context.latitude,
            "lon": context.longitude,
            "tz": context.timezone_name,
        },
        outputs={
            "weekday": kalam["weekday"],
            "rahu_kalam": kalam["rahu_kalam"],
        },
        steps=[
            {
                "step": "segment_day",
                "detail": "Segmented daylight into 8 windows by weekday mapping.",
            },
            {
                "step": "select_windows",
                "detail": "Picked Rahu Kalam, Yamaganda, and Gulika windows.",
            },
        ],
    )

    return {
        "date": context.target_date.isoformat(),
        "location": {
            "latitude": context.latitude,
            "longitude": context.longitude,
            "timezone": context.timezone_name,
        },
        "rahu_kalam": kalam["rahu_kalam"],
        "yamaganda": kalam["yamaganda"],
        "gulika": kalam["gulika"],
        "weekday": kalam["weekday"],
        "segment_model": kalam["segment_model"],
        "sunrise": kalam["sunrise"],
        "sunset": kalam["sunset"],
        "warnings": list(context.warnings),
        **base_meta_payload(
            trace_id=trace["trace_id"],
            confidence="computed",
            method="weekday_segment",
            method_profile="muhurta_v2_hora_chaughadia_tarabala",
            quality_band="validated",
            assumption_set_id="np-mainstream-v2",
            advisory_scope="ritual_planning",
        ),
    }


def build_auspicious_muhurta_response(
    *,
    date_str: str,
    ceremony_type: str,
    lat: CoordinateInput,
    lon: CoordinateInput,
    tz: Optional[str],
    birth_nakshatra: Optional[str],
    assumption_set: str,
) -> dict:
    context = _resolve_muhurta_request_context(date_str=date_str, lat=lat, lon=lon, tz=tz)
    ranked = get_auspicious_windows(
        context.target_date,
        lat=context.latitude,
        lon=context.longitude,
        ceremony_type=ceremony_type,
        tz_name=context.timezone_name,
        birth_nakshatra=birth_nakshatra,
        assumption_set_id=assumption_set,
    )

    trace = create_reason_trace(
        trace_type="muhurta_auspicious",
        subject={"date": context.target_date.isoformat(), "type": ceremony_type},
        inputs={
            "date": context.target_date.isoformat(),
            "type": ceremony_type,
            "lat": context.latitude,
            "lon": context.longitude,
            "tz": context.timezone_name,
            "birth_nakshatra": birth_nakshatra,
            "assumption_set": assumption_set,
        },
        outputs={
            "count": len(ranked["auspicious_muhurtas"]),
            "best_window": ranked["best_window"],
        },
        steps=[
            {"step": "day_night_muhurta", "detail": "Computed 30 day/night muhurta windows."},
            {
                "step": "hora_chaughadia",
                "detail": "Mapped each candidate to hora lord + chaughadia segment.",
            },
            {
                "step": "tara_bala",
                "detail": "Applied optional tara-bala signal from birth nakshatra.",
            },
            {
                "step": "score_rank",
                "detail": "Scored ceremony windows with assumption-set penalties/bonuses.",
            },
        ],
    )

    resolved_assumption_set = ranked.get("assumption_set_id", "np-mainstream-v2")
    enriched_ranked = [_enrich_ranked_window(row) for row in ranked["ranked_muhurtas"]]
    enriched_selected = [
        row for row in enriched_ranked if row["score"] >= ranked["ranking_profile"]["minimum_score"]
    ]

    if enriched_selected:
        best_window = enriched_selected[0]
    elif enriched_ranked:
        best_window = enriched_ranked[0]
    else:
        best_window = {}

    return {
        "date": context.target_date.isoformat(),
        "location": {
            "latitude": context.latitude,
            "longitude": context.longitude,
            "timezone": context.timezone_name,
        },
        "type": ranked["ceremony_type"],
        "muhurtas": enriched_selected,
        "ranked_muhurtas": enriched_ranked,
        "best_window": best_window,
        "reason_codes": best_window.get("reason_codes", []),
        "rank_explanation": best_window.get("rank_explanation"),
        "confidence_score": best_window.get("confidence_score", 0.0),
        "tara_bala": ranked["tara_bala"],
        "ranking_profile": ranked["ranking_profile"],
        "rahu_kalam": ranked["avoid"]["rahu_kalam"],
        "yamaganda": ranked["avoid"]["yamaganda"],
        "gulika": ranked["avoid"]["gulika"],
        "warnings": list(context.warnings),
        **base_meta_payload(
            trace_id=trace["trace_id"],
            confidence="computed",
            method="rule_ranked_muhurta_v2",
            method_profile="muhurta_v2_hora_chaughadia_tarabala",
            quality_band="validated",
            assumption_set_id=resolved_assumption_set,
            advisory_scope="ritual_planning",
        ),
    }


__all__ = [
    "build_auspicious_muhurta_response",
    "build_muhurta_for_day_response",
    "build_rahu_kalam_response",
]
