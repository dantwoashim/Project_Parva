"""Public-safe trust infrastructure API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Header, HTTPException, Query, Request
from pydantic import BaseModel, Field

from app.services.trust_infrastructure_service import (
    TrustInfrastructureError,
    build_compliance_decision_evidence_packet,
    build_date_conversion_evidence_packet,
    build_rule_execution_evidence_packet,
    diff_releases_payload,
    get_release_payload,
    get_source_payload,
    list_releases_payload,
    list_sources_payload,
    load_trust_log_payload,
    trust_capabilities_payload,
)

router = APIRouter(prefix="/api/trust", tags=["trust"])


class DateConversionEvidenceRequest(BaseModel):
    ad_date: str | None = Field(default=None, description="Gregorian date in YYYY-MM-DD format")
    bs_date: str | None = Field(default=None, description="Bikram Sambat date in YYYY-MM-DD format")
    release_id: str | None = Field(default=None, description="Optional public release id")


class ComplianceEvidenceRequest(BaseModel):
    profile_id: str = "nepal_private_company_default"
    bs_date: str | None = None
    ad_date: str | None = None
    decision_intent: str = "general"
    release_id: str | None = None


class RuleExecutionEvidenceRequest(BaseModel):
    rule_id: str = Field(..., examples=["last_working_day_of_nepali_month"])
    input: dict[str, Any] = Field(default_factory=dict)
    release_id: str | None = None


def _trace_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _release_id(query_value: str | None, header_value: str | None) -> str | None:
    return query_value or header_value


def _raise_trust_error(exc: TrustInfrastructureError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@router.get("/capabilities")
async def get_trust_capabilities() -> dict[str, Any]:
    return trust_capabilities_payload()


@router.get("/sources")
async def list_sources(
    release_id: str | None = Query(default=None),
    x_parva_release_id: str | None = Header(default=None),
) -> dict[str, Any]:
    try:
        return list_sources_payload(release_id=_release_id(release_id, x_parva_release_id))
    except TrustInfrastructureError as exc:
        _raise_trust_error(exc)


@router.get("/sources/{source_id}")
async def get_source(
    source_id: str,
    release_id: str | None = Query(default=None),
    x_parva_release_id: str | None = Header(default=None),
) -> dict[str, Any]:
    try:
        return get_source_payload(source_id, release_id=_release_id(release_id, x_parva_release_id))
    except TrustInfrastructureError as exc:
        _raise_trust_error(exc)


@router.get("/releases")
async def list_releases() -> dict[str, Any]:
    return list_releases_payload()


@router.get("/releases/{release_id}")
async def get_release(release_id: str) -> dict[str, Any]:
    try:
        return get_release_payload(release_id)
    except TrustInfrastructureError as exc:
        _raise_trust_error(exc)


@router.get("/releases/{from_release}/diff/{to_release}")
async def diff_releases(from_release: str, to_release: str) -> dict[str, Any]:
    try:
        return diff_releases_payload(from_release, to_release)
    except TrustInfrastructureError as exc:
        _raise_trust_error(exc)


@router.get("/log")
async def get_trust_log(
    release_id: str | None = Query(default=None),
    x_parva_release_id: str | None = Header(default=None),
) -> dict[str, Any]:
    try:
        return load_trust_log_payload(release_id=_release_id(release_id, x_parva_release_id))
    except TrustInfrastructureError as exc:
        _raise_trust_error(exc)


@router.post("/evidence/date-conversion")
async def create_date_conversion_evidence(
    payload: DateConversionEvidenceRequest,
    request: Request,
    release_id: str | None = Query(default=None),
    x_parva_release_id: str | None = Header(default=None),
) -> dict[str, Any]:
    try:
        return build_date_conversion_evidence_packet(
            release_id=_release_id(payload.release_id or release_id, x_parva_release_id),
            ad_date=payload.ad_date,
            bs_date=payload.bs_date,
            trace_id=_trace_id(request),
        )
    except TrustInfrastructureError as exc:
        _raise_trust_error(exc)


@router.post("/evidence/compliance-decision")
async def create_compliance_decision_evidence(
    payload: ComplianceEvidenceRequest,
    request: Request,
    release_id: str | None = Query(default=None),
    x_parva_release_id: str | None = Header(default=None),
) -> dict[str, Any]:
    try:
        return build_compliance_decision_evidence_packet(
            release_id=_release_id(payload.release_id or release_id, x_parva_release_id),
            profile_id=payload.profile_id,
            bs_date=payload.bs_date,
            ad_date=payload.ad_date,
            decision_intent=payload.decision_intent,
            trace_id=_trace_id(request),
        )
    except TrustInfrastructureError as exc:
        _raise_trust_error(exc)


@router.post("/evidence/rule-execution")
async def create_rule_execution_evidence(
    payload: RuleExecutionEvidenceRequest,
    request: Request,
    release_id: str | None = Query(default=None),
    x_parva_release_id: str | None = Header(default=None),
) -> dict[str, Any]:
    try:
        return build_rule_execution_evidence_packet(
            release_id=_release_id(payload.release_id or release_id, x_parva_release_id),
            rule_id=payload.rule_id,
            input_payload=payload.input,
            trace_id=_trace_id(request),
        )
    except TrustInfrastructureError as exc:
        _raise_trust_error(exc)
