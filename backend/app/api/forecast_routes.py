"""Long-horizon forecasting endpoints (Year-3 M28 baseline)."""

from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Query

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
        "note": "Forecast outputs include confidence decay metadata for long-horizon planning.",
        "policy": get_policy_metadata(),
    }


@router.get("/error-curve")
async def forecast_error_curve(
    start_year: int = Query(date.today().year, ge=1900, le=2300),
    end_year: int = Query(date.today().year + 25, ge=1900, le=2300),
):
    curve = build_error_curve(start_year, end_year)
    return {
        "start_year": min(start_year, end_year),
        "end_year": max(start_year, end_year),
        "points": curve,
        "policy": get_policy_metadata(),
    }
