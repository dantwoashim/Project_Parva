"""Agent-safe deterministic temporal API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.agent_service import (
    AgentError,
    agent_capabilities_payload,
    agent_manifest_payload,
    agent_tools_payload,
    check_human_review_payload,
    draft_rule_payload,
    explain_temporal_decision_payload,
    plan_schedule_payload,
    resolve_intent_payload,
    run_tool_payload,
    verify_temporal_claim_payload,
)
from app.services.impact_service import ImpactError
from app.services.rulelang_service import RuleLangError
from app.services.timegraph_service import TimeGraphError
from app.services.trust_infrastructure_service import TrustInfrastructureError

router = APIRouter(prefix="/api/agent", tags=["agent"])


class IntentRequest(BaseModel):
    text: str
    context: dict[str, Any] = Field(default_factory=dict)


class ClaimRequest(BaseModel):
    claim: str
    context: dict[str, Any] = Field(default_factory=dict)
    include_evidence: bool = False


class ScheduleRequest(BaseModel):
    schedule_type: str = "payroll_last_working_day"
    bs_year: int
    profile_id: str = "nepal_private_company_default"
    months: list[int] | None = None
    include_evidence: bool = False


class ExplainRequest(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)


class HumanReviewRequest(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)


class DraftRuleRequest(BaseModel):
    text: str
    profile_id: str = "nepal_private_company_default"


class RunToolRequest(BaseModel):
    tool_name: str
    input: dict[str, Any] = Field(default_factory=dict)


def _raise_agent_error(exc: Exception) -> None:
    status_code = getattr(exc, "status_code", 400)
    code = getattr(exc, "code", exc.__class__.__name__.upper())
    raise HTTPException(status_code=status_code, detail={"code": code, "message": str(exc)}) from exc


@router.get("/capabilities")
async def get_agent_capabilities() -> dict[str, Any]:
    return agent_capabilities_payload()


@router.get("/tools")
async def list_agent_tools() -> dict[str, Any]:
    return agent_tools_payload()


@router.get("/manifest")
async def get_agent_manifest() -> dict[str, Any]:
    return agent_manifest_payload()


@router.post("/resolve-intent")
async def resolve_intent(payload: IntentRequest) -> dict[str, Any]:
    try:
        return resolve_intent_payload(payload.text, context=payload.context)
    except AgentError as exc:
        _raise_agent_error(exc)


@router.post("/verify-claim")
async def verify_claim(payload: ClaimRequest) -> dict[str, Any]:
    try:
        return verify_temporal_claim_payload(
            payload.claim,
            context=payload.context,
            include_evidence=payload.include_evidence,
        )
    except (AgentError, TrustInfrastructureError) as exc:
        _raise_agent_error(exc)


@router.post("/plan-schedule")
async def plan_schedule(payload: ScheduleRequest) -> dict[str, Any]:
    try:
        return plan_schedule_payload(
            schedule_type=payload.schedule_type,
            bs_year=payload.bs_year,
            profile_id=payload.profile_id,
            months=payload.months,
            include_evidence=payload.include_evidence,
        )
    except (AgentError, RuleLangError) as exc:
        _raise_agent_error(exc)


@router.post("/explain")
async def explain(payload: ExplainRequest) -> dict[str, Any]:
    try:
        return explain_temporal_decision_payload(payload.payload)
    except (AgentError, RuleLangError) as exc:
        _raise_agent_error(exc)


@router.post("/check-human-review")
async def check_human_review(payload: HumanReviewRequest) -> dict[str, Any]:
    try:
        return check_human_review_payload(payload.payload)
    except AgentError as exc:
        _raise_agent_error(exc)


@router.post("/draft-rule")
async def draft_rule(payload: DraftRuleRequest) -> dict[str, Any]:
    try:
        return draft_rule_payload(payload.text, profile_id=payload.profile_id)
    except AgentError as exc:
        _raise_agent_error(exc)


@router.post("/run-tool")
async def run_tool(payload: RunToolRequest) -> dict[str, Any]:
    try:
        return run_tool_payload(payload.tool_name, payload.input)
    except (AgentError, RuleLangError, ImpactError, TimeGraphError, TrustInfrastructureError) as exc:
        _raise_agent_error(exc)
