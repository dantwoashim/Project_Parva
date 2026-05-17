"""Enterprise temporal compliance preview routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from app.membranes.capsule import (
    _proof_requested,
    build_holiday_capsule,
    build_working_day_capsule,
    proof_response,
)
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
from app.services.enterprise_calendar_service import parse_ad_date, parse_bs_date

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
async def evaluate_compliance_date(
    payload: ComplianceDateRequest,
    request: Request,
    proof: str | None = Query(None, description="Set to membrane/compact/audit/replay for a proof capsule."),
):
    try:
        response = evaluate_date_payload(
            profile_id=payload.profile_id,
            bs_date=payload.bs_date,
            ad_date=payload.ad_date,
            decision_intent=payload.decision_intent,
            trace_id=_trace_id(request),
        )
        proof_header = str(request.headers.get("x-parva-proof") or "").strip().lower()
        proof_mode = str(proof or proof_header or "").strip().lower()
        if _proof_requested(proof_mode):
            bs_year, bs_month, bs_day = parse_bs_date(response["date"]["bs"])
            response["proof"] = proof_response(
                build_working_day_capsule(
                    bs_year,
                    bs_month,
                    bs_day,
                    profile_id=payload.profile_id,
                    decision_intent=payload.decision_intent,
                ),
                mode=proof_mode or "membrane",
            )
        return response
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.get("/holiday")
async def holiday_lookup(
    request: Request,
    bs_date: str | None = Query(None, description="BS date in YYYY-MM-DD format."),
    ad_date: str | None = Query(None, description="AD date in YYYY-MM-DD format."),
    profile_id: str = Query("nepal_public_general"),
    proof: str | None = Query(None, description="Set to membrane/compact/audit/replay for a proof capsule."),
):
    """Check fixed public-corpus holiday membership with optional proof."""
    try:
        if bool(bs_date) == bool(ad_date):
            raise ValueError("Provide exactly one of bs_date or ad_date.")
        if bs_date:
            bs_year, bs_month, bs_day = parse_bs_date(bs_date)
        else:
            ad = parse_ad_date(str(ad_date))
            from app.calendar.bikram_sambat import gregorian_to_bs

            bs_year, bs_month, bs_day = gregorian_to_bs(ad)
        capsule = build_holiday_capsule(bs_year, bs_month, bs_day, profile_id=profile_id)
        response = {
            "bs_date": capsule["result"]["bs_date"],
            "profile_id": profile_id,
            "is_holiday": capsule["result"]["is_holiday"],
            "holiday": capsule["result"]["holiday"],
            "source_set": capsule["result"]["source_set"],
            "policy": capsule["policy_trace"],
            "meta": {
                "claim_boundary": "decision_support_not_authority",
                "trace_id": _trace_id(request),
            },
        }
        if _proof_requested(proof):
            response["proof"] = proof_response(capsule, mode=str(proof or "membrane"))
        return response
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
