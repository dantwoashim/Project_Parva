"""Public-safe RuleLang API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.services.rulelang_service import (
    RuleLangError,
    evaluate_custom_rule_payload,
    evaluate_rule_payload,
    explain_rule_payload,
    get_rule_payload,
    list_rules_payload,
    rulelang_capabilities_payload,
    test_rule_payload,
    validate_rule_payload,
)

from ._async_utils import run_cpu_bound

router = APIRouter(prefix="/api/rules", tags=["rules"])


class RuleValidateRequest(BaseModel):
    rule: dict[str, Any] = Field(..., description="Structured RuleLang rule definition")


class RuleEvaluateRequest(BaseModel):
    input: dict[str, Any] = Field(default_factory=dict, description="Rule input payload")
    release_id: str | None = Field(default=None, description="Optional public release id")
    include_evidence: bool = Field(default=False, description="Generate an evidence packet id when possible")


class CustomRuleEvaluateRequest(BaseModel):
    rule: dict[str, Any] = Field(..., description="Structured RuleLang rule definition")
    input: dict[str, Any] = Field(default_factory=dict, description="Rule input payload")
    release_id: str | None = None
    include_evidence: bool = False


class RuleExplainRequest(BaseModel):
    rule_id: str | None = Field(default=None, description="Public rule id to explain")
    rule: dict[str, Any] | None = Field(default=None, description="Optional custom public-safe rule")
    input: dict[str, Any] = Field(default_factory=dict, description="Rule input payload")
    release_id: str | None = None


def _trace_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _raise_rule_error(exc: RuleLangError) -> None:
    raise HTTPException(
        status_code=exc.status_code,
        detail={
            "code": exc.code,
            "message": str(exc),
            "details": exc.details,
        },
    ) from exc


@router.get("/capabilities")
async def get_rulelang_capabilities() -> dict[str, Any]:
    return rulelang_capabilities_payload()


@router.get("")
async def list_rules() -> dict[str, Any]:
    try:
        return list_rules_payload()
    except RuleLangError as exc:
        _raise_rule_error(exc)


@router.get("/{rule_id}")
async def get_rule(rule_id: str) -> dict[str, Any]:
    try:
        return get_rule_payload(rule_id)
    except RuleLangError as exc:
        _raise_rule_error(exc)


@router.post("/validate")
async def validate_rule(payload: RuleValidateRequest) -> dict[str, Any]:
    return validate_rule_payload(payload.rule)


@router.post("/{rule_id}/evaluate")
async def evaluate_rule(
    rule_id: str,
    payload: RuleEvaluateRequest,
    request: Request,
) -> dict[str, Any]:
    try:
        return await run_cpu_bound(
            evaluate_rule_payload,
            rule_id,
            payload.input,
            release_id=payload.release_id,
            trace_id=_trace_id(request),
            include_evidence=payload.include_evidence,
        )
    except RuleLangError as exc:
        _raise_rule_error(exc)


@router.post("/{rule_id}/test")
async def test_rule(rule_id: str, request: Request) -> dict[str, Any]:
    try:
        return await run_cpu_bound(test_rule_payload, rule_id, trace_id=_trace_id(request))
    except RuleLangError as exc:
        _raise_rule_error(exc)


@router.post("/evaluate")
async def evaluate_custom_rule(payload: CustomRuleEvaluateRequest, request: Request) -> dict[str, Any]:
    try:
        return await run_cpu_bound(
            evaluate_custom_rule_payload,
            payload.rule,
            payload.input,
            release_id=payload.release_id,
            trace_id=_trace_id(request),
            include_evidence=payload.include_evidence,
        )
    except RuleLangError as exc:
        _raise_rule_error(exc)


@router.post("/explain")
async def explain_rule(payload: RuleExplainRequest, request: Request) -> dict[str, Any]:
    try:
        if payload.rule is not None:
            result = await run_cpu_bound(
                evaluate_custom_rule_payload,
                payload.rule,
                payload.input,
                release_id=payload.release_id,
                trace_id=_trace_id(request),
            )
            return {
                "rule_id": result["rule_id"],
                "rule_version": result["rule_version"],
                "decision": result["decision"],
                "output": result["output"],
                "trace": result["trace"],
                "fact_ids": result["fact_ids"],
                "explanation": {
                    "summary": (
                        f"Rule {result['rule_id']} completed with status "
                        f"{result['decision']['status']}."
                    ),
                    "claim_boundary": result["meta"]["claim_boundary"],
                    "warnings": result["meta"]["warnings"],
                },
                "meta": result["meta"],
            }
        if not payload.rule_id:
            raise RuleLangError("rule_id or rule is required", code="INVALID_INPUT")
        return await run_cpu_bound(
            explain_rule_payload,
            payload.rule_id,
            payload.input,
            release_id=payload.release_id,
            trace_id=_trace_id(request),
        )
    except RuleLangError as exc:
        _raise_rule_error(exc)
