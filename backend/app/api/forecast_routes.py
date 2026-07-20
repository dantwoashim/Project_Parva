"""Long-horizon forecasting endpoints (Year-3 M28 baseline)."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query, Request

from app.api._clock import request_civil_date
from app.core.clock import DEFAULT_CIVIL_TIMEZONE
from app.forecast import build_error_curve, forecast_festivals, list_default_forecast_festivals
from app.policy import get_policy_metadata

router = APIRouter(prefix="/api/forecast", tags=["forecast"])


def _split_csv(raw: Optional[str]) -> list[str]:
    return [part.strip() for part in (raw or "").split(",") if part.strip()]


@router.get("/festivals")
async def forecast_festival_dates(
    year: int = Query(..., ge=2000, le=2200, description="Target Gregorian year"),
    festivals: Optional[str] = Query(
        None,
        description="Comma-separated festival ids. Defaults to priority set.",
    ),
):
    festival_ids = _split_csv(festivals) or list_default_forecast_festivals()
    items = forecast_festivals(year, festival_ids)

    return {
        "year": year,
        "count": len(items),
        "festivals": [item.__dict__ for item in items],
        "note": "Forecast outputs include heuristic confidence decay metadata for long-horizon planning.",
        "policy": get_policy_metadata(),
    }


@router.get("/error-curve")
async def forecast_error_curve(
    request: Request,
    start_year: int | None = Query(None, ge=1900, le=2300),
    end_year: int | None = Query(None, ge=1900, le=2300),
    tz: str = Query(DEFAULT_CIVIL_TIMEZONE, description="IANA timezone"),
):
    current_year = request_civil_date(request, tz).year
    resolved_start = start_year if start_year is not None else current_year
    resolved_end = end_year if end_year is not None else min(resolved_start + 25, 2300)
    curve = build_error_curve(resolved_start, resolved_end)
    return {
        "start_year": min(resolved_start, resolved_end),
        "end_year": max(resolved_start, resolved_end),
        "points": curve,
        "policy": get_policy_metadata(),
    }
