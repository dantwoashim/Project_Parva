"""Enterprise temporal compliance preview routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.services.compliance_service import (
    add_working_days_payload,
    evaluate_date_payload,
    fiscal_period_payload,
    get_profile_payload,
    list_profiles_payload,
    month_closing_day_payload,
    next_working_day_payload,
    previous_working_day_payload,
)

router = APIRouter(prefix="/api/compliance", tags=["compliance"])


class ComplianceDateRequest(BaseModel):
    profile_id: str = Field("nepal_private_company_default", examples=["nepal_private_company_default"])
    bs_date: str | None = Field(None, examples=["2082-04-02"])
    ad_date: str | None = Field(None, examples=["2025-07-18"])
    decision_intent: str = Field("general", examples=["general"])


class WorkingDaySearchRequest(BaseModel):
    profile_id: str = Field("nepal_private_company_default", examples=["nepal_private_company_default"])
    bs_date: str | None = Field(None, examples=["2082-04-03"])
    ad_date: str | None = Field(None, examples=["2025-07-19"])
    include_input: bool = False


class AddWorkingDaysRequest(BaseModel):
    profile_id: str = Field("nepal_private_company_default", examples=["nepal_private_company_default"])
    bs_date: str | None = Field(None, examples=["2082-04-02"])
    ad_date: str | None = Field(None, examples=["2025-07-18"])
    working_days: int = Field(..., ge=-366, le=366, examples=[5])


class MonthClosingDayRequest(BaseModel):
    profile_id: str = Field("nepal_private_company_default", examples=["nepal_private_company_default"])
    bs_year: int = Field(..., ge=1600, le=2600, examples=[2082])
    bs_month: int = Field(..., ge=1, le=12, examples=[4])


def _trace_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _bad_request(exc: ValueError) -> HTTPException:
    return HTTPException(status_code=400, detail=str(exc))


@router.get("/profiles")
async def list_compliance_profiles(request: Request):
    return list_profiles_payload(trace_id=_trace_id(request))


@router.get("/profiles/{profile_id}")
async def get_compliance_profile(profile_id: str, request: Request):
    try:
        return get_profile_payload(profile_id, trace_id=_trace_id(request))
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.post("/evaluate-date")
async def evaluate_compliance_date(payload: ComplianceDateRequest, request: Request):
    try:
        return evaluate_date_payload(
            profile_id=payload.profile_id,
            bs_date=payload.bs_date,
            ad_date=payload.ad_date,
            decision_intent=payload.decision_intent,
            trace_id=_trace_id(request),
        )
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.post("/next-working-day")
async def next_working_day(payload: WorkingDaySearchRequest, request: Request):
    try:
        return next_working_day_payload(
            profile_id=payload.profile_id,
            bs_date=payload.bs_date,
            ad_date=payload.ad_date,
            include_input=payload.include_input,
            trace_id=_trace_id(request),
        )
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.post("/previous-working-day")
async def previous_working_day(payload: WorkingDaySearchRequest, request: Request):
    try:
        return previous_working_day_payload(
            profile_id=payload.profile_id,
            bs_date=payload.bs_date,
            ad_date=payload.ad_date,
            include_input=payload.include_input,
            trace_id=_trace_id(request),
        )
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.post("/add-working-days")
async def add_working_days(payload: AddWorkingDaysRequest, request: Request):
    try:
        return add_working_days_payload(
            profile_id=payload.profile_id,
            bs_date=payload.bs_date,
            ad_date=payload.ad_date,
            working_days=payload.working_days,
            trace_id=_trace_id(request),
        )
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.post("/month-closing-day")
async def month_closing_day(payload: MonthClosingDayRequest, request: Request):
    try:
        return month_closing_day_payload(
            profile_id=payload.profile_id,
            bs_year=payload.bs_year,
            bs_month=payload.bs_month,
            trace_id=_trace_id(request),
        )
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.post("/fiscal-period")
async def fiscal_period(payload: ComplianceDateRequest, request: Request):
    try:
        return fiscal_period_payload(
            profile_id=payload.profile_id,
            bs_date=payload.bs_date,
            ad_date=payload.ad_date,
            trace_id=_trace_id(request),
        )
    except ValueError as exc:
        raise _bad_request(exc) from exc
