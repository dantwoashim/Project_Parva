"""Controlled Future BS audit, export, model-run, and impact routes."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field

from app.services.future_bs_service import (
    backtest_model,
    backtest_residuals,
    boundary_risk,
    compare_external_sheet,
    explain_month,
    full_backtest,
    import_excel_and_compare,
    model_run,
    model_runs,
    predict_bs_range,
    predict_bs_year,
    predictions_to_csv,
    predictions_to_xlsx,
    rolling_backtest,
    simulate_loan_impact,
)

from ._async_utils import run_cpu_bound

private_router = APIRouter(prefix="/v4/api/future-bs", tags=["future-bs-private"])


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
    day_count_method: Literal[
        "actual_365",
        "actual_360",
        "actual_actual",
        "30_360",
        "monthly_flat",
        "product_specific",
    ] = "actual_365"
    calendar_a: str = "external_sheet"
    calendar_b: str = "parva_prediction"
    external_years: list[ExternalYear] = Field(default_factory=list, max_length=250)


class ImportExcelRequest(BaseModel):
    source_name: str = Field(default="external_sheet", min_length=1, max_length=120)
    file_format: Literal["csv", "xlsx"]
    content_base64: str = Field(..., min_length=1)


def _bad_request(exc: ValueError) -> HTTPException:
    return HTTPException(status_code=400, detail=str(exc))


@private_router.get("/month-lengths/range")
async def future_bs_month_lengths_range(start: int, end: int):
    try:
        return await run_cpu_bound(predict_bs_range, start, end)
    except ValueError as exc:
        raise _bad_request(exc) from exc


@private_router.post("/month-lengths/compare")
async def future_bs_compare_month_lengths(payload: CompareMonthLengthsRequest):
    try:
        return await run_cpu_bound(
            compare_external_sheet,
            payload.source_name,
            [year.model_dump() for year in payload.years],
        )
    except ValueError as exc:
        raise _bad_request(exc) from exc


@private_router.post("/month-lengths/import-excel")
async def future_bs_import_excel(payload: ImportExcelRequest):
    try:
        return await run_cpu_bound(
            import_excel_and_compare,
            payload.source_name,
            payload.content_base64,
            payload.file_format,
        )
    except ValueError as exc:
        raise _bad_request(exc) from exc


@private_router.get("/month-lengths/backtest")
async def future_bs_backtest(
    train_start: int,
    train_end: int,
    test_start: int,
    test_end: int,
    source_policy: Literal[
        "all_reference",
        "official_only",
        "official_plus_printed",
        "train_allowed",
    ] = "all_reference",
):
    try:
        return await run_cpu_bound(
            backtest_model,
            train_start,
            train_end,
            test_start,
            test_end,
            source_policy=source_policy,
        )
    except ValueError as exc:
        raise _bad_request(exc) from exc


@private_router.get("/backtest")
async def future_bs_backtest_v2(
    mode: Literal["holdout", "full", "rolling"] = "holdout",
    train_start: int = 2040,
    train_end: int = 2075,
    test_start: int = 2076,
    test_end: int = 2083,
    source_policy: Literal[
        "all_reference",
        "official_only",
        "official_plus_printed",
        "train_allowed",
    ] = "all_reference",
):
    try:
        if mode == "full":
            return await run_cpu_bound(full_backtest, test_start, test_end, source_policy=source_policy)
        if mode == "rolling":
            return await run_cpu_bound(
                rolling_backtest,
                train_start,
                test_start,
                test_end,
                source_policy=source_policy,
            )
        return await run_cpu_bound(
            backtest_model,
            train_start,
            train_end,
            test_start,
            test_end,
            source_policy=source_policy,
        )
    except ValueError as exc:
        raise _bad_request(exc) from exc


@private_router.get("/backtest/residuals")
async def future_bs_backtest_residuals(
    train_start: int,
    train_end: int,
    test_start: int,
    test_end: int,
    source_policy: Literal[
        "all_reference",
        "official_only",
        "official_plus_printed",
        "train_allowed",
    ] = "all_reference",
):
    try:
        return await run_cpu_bound(
            backtest_residuals,
            train_start,
            train_end,
            test_start,
            test_end,
            source_policy=source_policy,
        )
    except ValueError as exc:
        raise _bad_request(exc) from exc


@private_router.get("/month-lengths/explain")
async def future_bs_explain_month(year: int, month: int):
    try:
        return await run_cpu_bound(explain_month, year, month)
    except ValueError as exc:
        raise _bad_request(exc) from exc


@private_router.get("/boundary-risk")
async def future_bs_boundary_risk(year: int, month: int):
    try:
        return await run_cpu_bound(boundary_risk, year, month)
    except ValueError as exc:
        raise _bad_request(exc) from exc


@private_router.get("/month-lengths/export.csv")
async def future_bs_export_csv(start: int, end: int):
    try:
        body = await run_cpu_bound(predictions_to_csv, start, end)
    except ValueError as exc:
        raise _bad_request(exc) from exc
    filename = f"parva_future_bs_{start}_{end}.csv"
    return Response(
        content=body,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@private_router.get("/export.csv")
async def future_bs_export_csv_alias(start: int, end: int):
    return await future_bs_export_csv(start, end)


@private_router.get("/month-lengths/export.xlsx")
async def future_bs_export_xlsx(start: int, end: int):
    try:
        body = await run_cpu_bound(predictions_to_xlsx, start, end)
    except ValueError as exc:
        raise _bad_request(exc) from exc
    filename = f"parva_future_bs_{start}_{end}.xlsx"
    return Response(
        content=body,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@private_router.get("/export.xlsx")
async def future_bs_export_xlsx_alias(start: int, end: int):
    return await future_bs_export_xlsx(start, end)


@private_router.get("/month-lengths/{bs_year}")
async def future_bs_month_lengths(bs_year: int):
    try:
        return await run_cpu_bound(predict_bs_year, bs_year)
    except ValueError as exc:
        raise _bad_request(exc) from exc


@private_router.post("/loan-impact/simulate")
async def future_bs_loan_impact(payload: LoanImpactRequest):
    raw_payload: dict[str, Any] = payload.model_dump()
    try:
        return await run_cpu_bound(simulate_loan_impact, raw_payload)
    except ValueError as exc:
        raise _bad_request(exc) from exc


@private_router.get("/model-runs")
async def future_bs_model_runs():
    return {"runs": await run_cpu_bound(model_runs)}


@private_router.get("/model-runs/{run_id}")
async def future_bs_model_run(run_id: str):
    try:
        return await run_cpu_bound(model_run, run_id)
    except ValueError as exc:
        raise _bad_request(exc) from exc


router = private_router
