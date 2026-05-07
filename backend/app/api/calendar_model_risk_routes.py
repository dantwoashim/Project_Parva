"""Calendar Model-Risk API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.calendar_model_risk_service import (
    audit_external_sheet_response,
    calendar_var_response,
    capabilities_payload,
    claim_readiness_report,
    committee_posterior_payload,
    perturbation_response,
    prediction_payload,
    prediction_set_response,
    replay_2083_ashwin,
    stress_test_response,
)

router = APIRouter(prefix="/v5/api/calendar-model-risk", tags=["calendar-model-risk"])


class ExternalYear(BaseModel):
    bs_year: int
    months: list[int] = Field(..., min_length=12, max_length=12)


class ExternalSheetAuditRequest(BaseModel):
    source_name: str = "external_sheet"
    years: list[ExternalYear] = Field(default_factory=list, max_length=250)


class CalendarVarRequest(BaseModel):
    bs_year: int
    month: int = Field(..., ge=1, le=12)
    principal: float = Field(default=0.0, ge=0)
    annual_rate: float = Field(default=0.0, ge=0)
    affected_contracts: int = Field(default=1, ge=1)
    operational_irreversibility_score: float = Field(default=1.0, ge=0)
    official_publication_delay_risk: float = Field(default=1.0, ge=0)


def _bad_request(exc: ValueError) -> HTTPException:
    return HTTPException(status_code=400, detail=str(exc))


@router.get("/capabilities")
async def calendar_model_risk_capabilities():
    return capabilities_payload()


@router.get("/prediction/{bs_year}/{month}")
async def calendar_model_risk_prediction(bs_year: int, month: int):
    try:
        return prediction_payload(bs_year, month)
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.get("/prediction-set/{bs_year}/{month}")
async def calendar_model_risk_prediction_set(bs_year: int, month: int):
    try:
        return prediction_set_response(bs_year, month)
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.get("/committee-posterior/{bs_year}/{month}")
async def calendar_model_risk_committee_posterior(bs_year: int, month: int):
    try:
        return committee_posterior_payload(bs_year, month)
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.get("/perturbation-robustness/{bs_year}/{month}")
async def calendar_model_risk_perturbation(bs_year: int, month: int):
    try:
        return perturbation_response(bs_year, month)
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.post("/audit-external-sheet")
async def calendar_model_risk_audit_external_sheet(payload: ExternalSheetAuditRequest):
    try:
        return audit_external_sheet_response(payload.model_dump())
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.post("/calendar-var")
async def calendar_model_risk_calendar_var(payload: CalendarVarRequest):
    try:
        return calendar_var_response(payload.model_dump())
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.post("/stress-test")
async def calendar_model_risk_stress_test(payload: CalendarVarRequest):
    try:
        return stress_test_response(payload.model_dump())
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.get("/red-team/2083-ashwin")
async def calendar_model_risk_2083_ashwin():
    return replay_2083_ashwin()


@router.get("/claim-readiness")
async def calendar_model_risk_claim_readiness():
    return claim_readiness_report()


@router.get("/reports/{report_id}")
async def calendar_model_risk_report(report_id: str) -> dict[str, Any]:
    if report_id == "claim-readiness":
        return claim_readiness_report()
    if report_id == "red-team-2083-ashwin":
        return replay_2083_ashwin()
    raise HTTPException(status_code=404, detail="unknown report_id")
