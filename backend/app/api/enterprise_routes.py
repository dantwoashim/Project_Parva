"""Enterprise calendar evaluation routes."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.enterprise_calendar_service import (
    bs_months_payload,
    bulk_convert_payload,
    business_days_payload,
    capabilities_payload,
    fiscal_year_payload,
    validate_cases_payload,
)

router = APIRouter(prefix="/api/enterprise", tags=["enterprise"])


class BusinessDaysRequest(BaseModel):
    start_bs: str = Field(..., examples=["2082-04-01"])
    end_bs: str = Field(..., examples=["2082-04-31"])
    weekend: str = "saturday"
    include_start: bool = True
    include_end: bool = True
    holiday_policy: str = "none"


class BulkConvertRequest(BaseModel):
    mode: Literal["ad_to_bs", "bs_to_ad"]
    dates: list[str] = Field(..., min_length=1, max_length=500)


class ValidationCase(BaseModel):
    id: str
    type: Literal["ad_to_bs", "bs_to_ad"]
    input: str
    expected: str | None = None


class ValidateRequest(BaseModel):
    cases: list[ValidationCase] = Field(..., min_length=1, max_length=500)


def _bad_request(exc: ValueError) -> HTTPException:
    return HTTPException(status_code=400, detail=str(exc))


@router.get("/capabilities")
async def enterprise_capabilities():
    return capabilities_payload()


@router.get("/fiscal-year/{bs_year}")
async def enterprise_fiscal_year(bs_year: int):
    try:
        return fiscal_year_payload(bs_year)
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.get("/bs-months/{bs_year}")
async def enterprise_bs_months(bs_year: int):
    try:
        return bs_months_payload(bs_year)
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.post("/business-days")
async def enterprise_business_days(payload: BusinessDaysRequest):
    try:
        return business_days_payload(
            start_bs=payload.start_bs,
            end_bs=payload.end_bs,
            weekend=payload.weekend,
            include_start=payload.include_start,
            include_end=payload.include_end,
            holiday_policy=payload.holiday_policy,
        )
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.post("/bulk-convert")
async def enterprise_bulk_convert(payload: BulkConvertRequest):
    try:
        return bulk_convert_payload(payload.mode, payload.dates)
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.post("/validate")
async def enterprise_validate(payload: ValidateRequest):
    return validate_cases_payload([case.model_dump() for case in payload.cases])
