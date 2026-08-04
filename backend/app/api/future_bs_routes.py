"""Curated public Future BS research routes."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.services.future_bs_public_service import (
    future_bs_capabilities_payload,
    future_bs_forecast_payload,
    future_bs_methodology_payload,
)

public_router = APIRouter(prefix="/v4/api/future-bs", tags=["future-bs"])


class FutureBSMonthForecast(BaseModel):
    month: int = Field(..., ge=1, le=12)
    month_name: str
    predicted_days: int = Field(..., ge=29, le=32)
    prediction_set_80: list[int]
    prediction_set_95: list[int]
    model_probability: dict[str, float]
    heuristic_confidence_score: float = Field(..., ge=0, le=1)
    confidence_label: str
    model_agreement: str
    boundary_distance_minutes: int | None = None
    risk_label: Literal["GREEN", "YELLOW", "RED"]
    risk_flags: list[str]


class FutureBSForecastResponse(BaseModel):
    bs_year: int
    month_lengths: list[int] = Field(..., min_length=12, max_length=12)
    months: list[FutureBSMonthForecast] = Field(..., min_length=12, max_length=12)
    year_total_days: int = Field(..., ge=365, le=366)
    heuristic_confidence_score: float = Field(..., ge=0, le=1)
    confidence_label: str
    risk_flags: list[str]
    constraints: dict[str, Any]
    surface: Literal["future_bs_public_forecast"]
    status: Literal["research_preview"]
    maturity: Literal["research_preview"]
    publication_status: Literal["computed_prediction_not_official"]
    review_required: Literal[True]
    authoritative_publication_overrides: Literal[True]
    snapshot_id: str
    method: dict[str, Any]
    risk_summary: dict[str, int]
    validation: dict[str, Any]
    limits: dict[str, Any]
    meta: dict[str, Any]


def _bad_request(exc: ValueError) -> HTTPException:
    return HTTPException(status_code=400, detail=str(exc))


@public_router.get("/capabilities")
async def future_bs_capabilities(request: Request):
    return future_bs_capabilities_payload(trace_id=getattr(request.state, "request_id", None))


@public_router.get("/methodology")
async def future_bs_methodology(request: Request):
    return future_bs_methodology_payload(trace_id=getattr(request.state, "request_id", None))


@public_router.get("/forecast/{bs_year}", response_model=FutureBSForecastResponse)
async def future_bs_forecast(bs_year: int, request: Request):
    try:
        return future_bs_forecast_payload(
            bs_year,
            trace_id=getattr(request.state, "request_id", None),
        )
    except ValueError as exc:
        raise _bad_request(exc) from exc


router = public_router
