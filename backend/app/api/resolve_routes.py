"""Unified temporal resolution endpoint for v5 authority track."""

from __future__ import annotations

from datetime import date, datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from app.api.v5_types import ResolveResult
from app.calendar.bikram_sambat import (
    get_bs_confidence,
    get_bs_estimated_error_days,
    get_bs_month_name,
    get_bs_source_range,
    gregorian_to_bs,
)
from app.calendar.panchanga import get_panchanga
from app.calendar.tithi.tithi_udaya import get_udaya_tithi
from app.explainability.store import create_reason_trace
from app.rules import get_rule_service

router = APIRouter(prefix="/api", tags=["resolve"])


def _parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid date format, use YYYY-MM-DD") from exc


def _build_bs_payload(target_date: date) -> dict:
    bs_year, bs_month, bs_day = gregorian_to_bs(target_date)
    return {
        "year": bs_year,
        "month": bs_month,
        "day": bs_day,
        "month_name": get_bs_month_name(bs_month),
        "confidence": get_bs_confidence(target_date),
        "source_range": get_bs_source_range(target_date),
        "estimated_error_days": get_bs_estimated_error_days(target_date),
    }


def _build_tithi_payload(target_date: date, latitude: float, longitude: float) -> dict:
    udaya = get_udaya_tithi(target_date, latitude=latitude, longitude=longitude)
    return {
        "display_number": udaya.get("tithi"),
        "absolute_number": udaya.get("tithi_absolute"),
        "name": udaya.get("name"),
        "paksha": udaya.get("paksha"),
        "method": "ephemeris_udaya",
        "sunrise_local": udaya.get("sunrise_local").isoformat()
        if udaya.get("sunrise_local")
        else None,
        "sunrise_utc": udaya.get("sunrise").isoformat() if udaya.get("sunrise") else None,
        "progress": udaya.get("progress"),
    }


def _build_panchanga_payload(target_date: date) -> dict:
    panchanga_raw = get_panchanga(target_date)
    return {
        "tithi": panchanga_raw.get("tithi", {}),
        "nakshatra": panchanga_raw.get("nakshatra", {}),
        "yoga": panchanga_raw.get("yoga", {}),
        "karana": panchanga_raw.get("karana", {}),
        "vaara": panchanga_raw.get("vaara", {}),
        "sunrise": panchanga_raw.get("sunrise", {}),
        "ephemeris_mode": panchanga_raw.get("mode", "swiss_moshier"),
    }


def _build_observances_payload(target_date: date) -> list[dict]:
    observances = []
    rule_service = get_rule_service()
    for festival_id, window in rule_service.on_date(target_date):
        observances.append(
            {
                "festival_id": festival_id,
                "start_date": window.start_date.isoformat(),
                "end_date": window.end_date.isoformat(),
                "method": window.method,
            }
        )
    return observances


def _build_trace_payload(
    *,
    target_date: date,
    profile: str,
    latitude: float,
    longitude: float,
    bs: dict,
    tithi: dict,
    observances: list[dict],
) -> dict:
    trace_payload = create_reason_trace(
        trace_type="resolve_context",
        subject={"date": target_date.isoformat(), "profile": profile},
        inputs={
            "latitude": latitude,
            "longitude": longitude,
            "timezone": "Asia/Kathmandu",
        },
        outputs={
            "bs": bs,
            "tithi": {
                "display_number": tithi["display_number"],
                "paksha": tithi["paksha"],
                "name": tithi["name"],
            },
            "observance_count": len(observances),
        },
        steps=[
            {
                "step_type": "bs_conversion",
                "math_expression": "gregorian_to_bs(date)",
                "output": bs,
            },
            {
                "step_type": "udaya_tithi",
                "math_expression": "tithi_at_sunrise(date, lat, lon)",
                "output": tithi,
            },
            {
                "step_type": "festival_resolution",
                "math_expression": "rules.on_date(date)",
                "output": {"count": len(observances)},
            },
        ],
        provenance={
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": "resolve_endpoint_v5_track",
        },
    )
    return {
        "trace_id": trace_payload.get("trace_id"),
        "trace_type": trace_payload.get("trace_type"),
        "subject": trace_payload.get("subject", {}),
        "inputs": trace_payload.get("inputs", {}),
        "outputs": trace_payload.get("outputs", {}),
        "steps": trace_payload.get("steps", []),
        "provenance": trace_payload.get("provenance", {}),
    }


@router.get("/resolve", response_model=ResolveResult)
async def resolve_temporal_context(
    date_value: str = Query(..., alias="date", description="Gregorian date YYYY-MM-DD"),
    profile: str = Query("np-mainstream", description="Observance profile"),
    latitude: float = Query(27.7172, ge=-90.0, le=90.0),
    longitude: float = Query(85.3240, ge=-180.0, le=180.0),
    include_trace: bool = Query(True),
):
    """
    Resolve date context into BS + panchanga + observances in one request.

    This endpoint is intended as the authority-style one-shot resolution API for
    consumers that need deterministic, replayable context with minimal round trips.
    """
    target_date = _parse_date(date_value)
    bs = _build_bs_payload(target_date)
    tithi = _build_tithi_payload(target_date, latitude, longitude)
    panchanga = _build_panchanga_payload(target_date)
    observances = _build_observances_payload(target_date)
    trace = (
        _build_trace_payload(
            target_date=target_date,
            profile=profile,
            latitude=latitude,
            longitude=longitude,
            bs=bs,
            tithi=tithi,
            observances=observances,
        )
        if include_trace
        else None
    )

    return ResolveResult(
        date=target_date.isoformat(),
        profile=profile,
        location={
            "latitude": latitude,
            "longitude": longitude,
            "timezone": "Asia/Kathmandu",
        },
        bikram_sambat=bs,
        tithi=tithi,
        panchanga=panchanga,
        observances=observances,
        trace=trace,
    )
