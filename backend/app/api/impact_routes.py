"""Public-safe temporal impact API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.services.impact_service import (
    ImpactError,
    event_schema_payload,
    impact_capabilities_payload,
    reason_codes_payload,
    recommended_actions_payload,
    semantic_release_diff_payload,
    simulate_change_set_payload,
    simulate_release_diff_payload,
)

from ._async_utils import run_cpu_bound

router = APIRouter(prefix="/api/impact", tags=["impact"])


class ReleaseDiffRequest(BaseModel):
    from_release_id: str = Field(default="parva-bs-public-demo")
    to_release_id: str = Field(default="parva-bs-public-demo")
    include_fixture: bool = Field(default=False)


class ChangeSetRequest(BaseModel):
    change_set: dict[str, Any] = Field(default_factory=dict)
    limit: int = Field(default=100, ge=1, le=1000)


class ReleaseDiffSimulationRequest(ReleaseDiffRequest):
    limit: int = Field(default=100, ge=1, le=1000)


def _raise_impact_error(exc: ImpactError) -> None:
    raise HTTPException(
        status_code=exc.status_code,
        detail={"code": "IMPACT_ERROR", "message": str(exc)},
    ) from exc


@router.get("/capabilities")
async def get_impact_capabilities() -> dict[str, Any]:
    return impact_capabilities_payload()


@router.post("/diff-releases")
async def diff_releases(payload: ReleaseDiffRequest) -> dict[str, Any]:
    try:
        return await run_cpu_bound(
            semantic_release_diff_payload,
            payload.from_release_id,
            payload.to_release_id,
            include_fixture=payload.include_fixture,
        )
    except ImpactError as exc:
        _raise_impact_error(exc)


@router.post("/simulate-change-set")
async def simulate_change_set(payload: ChangeSetRequest, request: Request) -> dict[str, Any]:
    try:
        change_set = dict(payload.change_set)
        change_set.setdefault("trace_id", getattr(request.state, "request_id", None))
        return await run_cpu_bound(simulate_change_set_payload, change_set, limit=payload.limit)
    except ImpactError as exc:
        _raise_impact_error(exc)


@router.post("/simulate-release-diff")
async def simulate_release_diff(payload: ReleaseDiffSimulationRequest) -> dict[str, Any]:
    try:
        return await run_cpu_bound(
            simulate_release_diff_payload,
            payload.from_release_id,
            payload.to_release_id,
            include_fixture=payload.include_fixture,
            limit=payload.limit,
        )
    except ImpactError as exc:
        _raise_impact_error(exc)


@router.get("/runs/{impact_run_id}")
async def get_impact_run(impact_run_id: str) -> dict[str, Any]:
    raise HTTPException(
        status_code=404,
        detail={
            "code": "IMPACT_RUN_NOT_STORED",
            "message": "Public preview impact runs are deterministic response objects and are not persisted.",
            "impact_run_id": impact_run_id,
        },
    )


@router.get("/reason-codes")
async def get_impact_reason_codes() -> dict[str, Any]:
    return reason_codes_payload()


@router.get("/recommended-actions")
async def get_impact_recommended_actions() -> dict[str, Any]:
    return recommended_actions_payload()


@router.get("/event-schema")
async def get_impact_event_schema() -> dict[str, Any]:
    return event_schema_payload()
