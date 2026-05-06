"""Future BS month-length prediction and financial-risk routes."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field

from app.services.future_bs_service import (
    CALIBRATION_VERSION,
    METHOD_VERSION,
    backtest_model,
    compare_external_sheet,
    explain_month,
    predict_bs_range,
    predict_bs_year,
    predictions_to_csv,
    predictions_to_xlsx,
    simulate_loan_impact,
)

router = APIRouter(prefix="/v4/api/future-bs", tags=["future-bs"])


class ExternalYear(BaseModel):
    bs_year: int
    months: list[int] = Field(..., min_length=12, max_length=12)


class CompareMonthLengthsRequest(BaseModel):
    source_name: str = Field(default="external_sheet", min_length=1, max_length=120)
    years: list[ExternalYear] = Field(..., min_length=1, max_length=250)


class LoanImpactRequest(BaseModel):
    loan_start_bs: str = Field(..., examples=["2084-01-15"])
    term_months: int = Field(..., ge=1, le=600)
    principal: float = Field(..., ge=0)
    annual_rate: float = Field(..., ge=0)
    day_count_method: Literal["actual_365"] = "actual_365"
    calendar_a: str = "external_sheet"
    calendar_b: str = "parva_prediction"
    external_years: list[ExternalYear] = Field(default_factory=list, max_length=250)


def _bad_request(exc: ValueError) -> HTTPException:
    return HTTPException(status_code=400, detail=str(exc))


@router.get("/capabilities")
async def future_bs_capabilities():
    return {
        "surface": "future_bs_month_length_validation",
        "status": "evaluation_ready",
        "core_product": "BS year -> 12 month lengths -> confidence -> mismatch report -> loan impact",
        "stable": [
            "known_static_corpus_month_lengths",
            "probabilistic_future_month_length_prediction",
            "external_sheet_comparison",
            "month_level_explainability",
            "loan_interest_impact_simulation",
            "csv_export",
            "xlsx_export",
        ],
        "computed": [
            "future_month_lengths_beyond_static_lookup",
            "confidence_scores",
            "risk_flags",
            "backtest_metrics",
        ],
        "not_claimed": [
            "official_future_publication",
            "legal_or_tax_final_authority",
            "JPL-backed production solar-ingress certification",
        ],
        "method_version": METHOD_VERSION,
        "calibration_version": CALIBRATION_VERSION,
        "recommended_use": [
            "technical validation",
            "InfoDevelopers Excel comparison",
            "loan-contract calendar-risk screening",
            "manual-review prioritization",
        ],
    }


@router.get("/month-lengths/range")
async def future_bs_month_lengths_range(start: int, end: int):
    try:
        return predict_bs_range(start, end)
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.post("/month-lengths/compare")
async def future_bs_compare_month_lengths(payload: CompareMonthLengthsRequest):
    try:
        return compare_external_sheet(
            payload.source_name,
            [year.model_dump() for year in payload.years],
        )
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.get("/month-lengths/backtest")
async def future_bs_backtest(train_start: int, train_end: int, test_start: int, test_end: int):
    try:
        return backtest_model(train_start, train_end, test_start, test_end)
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.get("/month-lengths/explain")
async def future_bs_explain_month(year: int, month: int):
    try:
        return explain_month(year, month)
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.get("/month-lengths/export.csv")
async def future_bs_export_csv(start: int, end: int):
    try:
        body = predictions_to_csv(start, end)
    except ValueError as exc:
        raise _bad_request(exc) from exc
    filename = f"parva_future_bs_{start}_{end}.csv"
    return Response(
        content=body,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/month-lengths/export.xlsx")
async def future_bs_export_xlsx(start: int, end: int):
    try:
        body = predictions_to_xlsx(start, end)
    except ValueError as exc:
        raise _bad_request(exc) from exc
    filename = f"parva_future_bs_{start}_{end}.xlsx"
    return Response(
        content=body,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/month-lengths/{bs_year}")
async def future_bs_month_lengths(bs_year: int):
    try:
        return predict_bs_year(bs_year)
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.post("/loan-impact/simulate")
async def future_bs_loan_impact(payload: LoanImpactRequest):
    raw_payload: dict[str, Any] = payload.model_dump()
    try:
        return simulate_loan_impact(raw_payload)
    except ValueError as exc:
        raise _bad_request(exc) from exc
