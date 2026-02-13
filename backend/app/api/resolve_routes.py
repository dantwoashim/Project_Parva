"""Unified temporal resolution endpoint for v5 authority track."""

from __future__ import annotations

from datetime import date, datetime, timezone
from fastapi import APIRouter, HTTPException, Query

from app.calendar.bikram_sambat import (
    get_bs_confidence,
    get_bs_estimated_error_days,
    get_bs_month_name,
    get_bs_source_range,
    gregorian_to_bs,
)
from app.calendar.tithi.tithi_udaya import get_udaya_tithi
from app.calendar.panchanga import get_panchanga
from app.explainability.store import create_reason_trace
from app.rules import get_rule_service
from app.api.v5_types import ResolveResult


router = APIRouter(prefix="/api", tags=["resolve"])


def _parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid date format, use YYYY-MM-DD") from exc


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

    bs_year, bs_month, bs_day = gregorian_to_bs(target_date)
    bs = {
        "year": bs_year,
        "month": bs_month,
        "day": bs_day,
        "month_name": get_bs_month_name(bs_month),
        "confidence": get_bs_confidence(target_date),
        "source_range": get_bs_source_range(target_date),
        "estimated_error_days": get_bs_estimated_error_days(target_date),
    }

    udaya = get_udaya_tithi(target_date, latitude=latitude, longitude=longitude)
    tithi = {
        "display_number": udaya.get("tithi"),
        "absolute_number": udaya.get("tithi_absolute"),
        "name": udaya.get("name"),
        "paksha": udaya.get("paksha"),
        "method": "ephemeris_udaya",
        "sunrise_local": udaya.get("sunrise_local").isoformat() if udaya.get("sunrise_local") else None,
        "sunrise_utc": udaya.get("sunrise").isoformat() if udaya.get("sunrise") else None,
        "progress": udaya.get("progress"),
    }

    panchanga_raw = get_panchanga(target_date)
    panchanga = {
        "tithi": panchanga_raw.get("tithi", {}),
        "nakshatra": panchanga_raw.get("nakshatra", {}),
        "yoga": panchanga_raw.get("yoga", {}),
        "karana": panchanga_raw.get("karana", {}),
        "vaara": panchanga_raw.get("vaara", {}),
        "sunrise": panchanga_raw.get("sunrise", {}),
        "ephemeris_mode": panchanga_raw.get("mode", "swiss_moshier"),
    }

    rule_service = get_rule_service()
    observances = []
    for festival_id, window in rule_service.on_date(target_date):
        observances.append(
            {
                "festival_id": festival_id,
                "start_date": window.start_date.isoformat(),
                "end_date": window.end_date.isoformat(),
                "method": window.method,
            }
        )

    trace = None
    if include_trace:
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
        trace = {
            "trace_id": trace_payload.get("trace_id"),
            "trace_type": trace_payload.get("trace_type"),
            "subject": trace_payload.get("subject", {}),
            "inputs": trace_payload.get("inputs", {}),
            "outputs": trace_payload.get("outputs", {}),
            "steps": trace_payload.get("steps", []),
            "provenance": trace_payload.get("provenance", {}),
        }

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
