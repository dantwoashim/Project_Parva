"""Public-safe TimeGraph API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from app.services.timegraph_service import (
    MAX_LIMIT,
    TimeGraphError,
    get_fact_payload,
    get_facts_for_date_payload,
    get_facts_for_profile_payload,
    get_facts_for_release_payload,
    get_facts_for_source_payload,
    get_relationships_payload,
    list_conflicts_payload,
    list_facts_payload,
    query_facts_payload,
    timegraph_capabilities_payload,
    trace_fact_payload,
)
from app.services.trust_infrastructure_service import TrustInfrastructureError

from ._async_utils import run_cpu_bound

router = APIRouter(prefix="/api/timegraph", tags=["timegraph"])


class TimeGraphMetadata(BaseModel):
    release_id: str
    confidence: str
    claim_boundary: str
    warnings: list[str]
    trace_id: str | None = None


class TemporalFact(BaseModel):
    fact_id: str
    fact_type: str
    subject: dict[str, Any]
    predicate: str
    object: dict[str, Any]
    release_id: str
    source_ids: list[str]
    confidence: str
    claim_boundary: str
    warnings: list[str]
    jurisdiction: str | None = None
    profile_ids: list[str] = Field(default_factory=list)
    validity: dict[str, str | None]
    metadata: dict[str, Any] = Field(default_factory=dict)


class TimeGraphRelationship(BaseModel):
    relationship_id: str
    from_id: str
    to_id: str
    type: str
    release_id: str
    confidence: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class TimeGraphConflict(BaseModel):
    conflict_id: str
    conflict_type: str
    status: str
    facts: list[str]
    sources: list[str]
    release_ids: list[str]
    summary: str
    resolution_policy: str
    requires_human_review: bool
    confidence: str
    warnings: list[str]
    metadata: dict[str, Any] = Field(default_factory=dict)


class TimeGraphQuery(BaseModel):
    release_id: str | None = None
    fact_type: str | None = None
    date: str | None = None
    calendar: str | None = None
    source_id: str | None = None
    profile_id: str | None = None
    confidence: str | None = None
    claim_boundary: str | None = None
    jurisdiction: str | None = None
    has_conflicts: bool | None = None
    limit: int = Field(default=50, ge=1, le=MAX_LIMIT)
    offset: int = Field(default=0, ge=0)


class TimeGraphCapabilities(BaseModel):
    surface: str
    status: str
    active_release_id: str
    fact_types: list[str]
    relationship_types: list[str]
    default_limit: int
    max_limit: int
    trace_depth: dict[str, int]
    claim_boundary: str
    warnings: list[str]


class TimeGraphTrace(BaseModel):
    fact_id: str
    fact: dict[str, Any]
    sources: list[dict[str, Any]]
    release: dict[str, Any]
    derived_from: list[dict[str, Any]]
    relationships: list[dict[str, Any]]
    evidence_packets: list[dict[str, Any]]
    conflicts: list[dict[str, Any]]
    confidence: str
    warnings: list[str]
    claim_boundary: str
    trace_depth: int


def _trace_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _raise_timegraph_error(exc: TimeGraphError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@router.get("/capabilities", response_model=TimeGraphCapabilities)
async def get_timegraph_capabilities() -> dict[str, Any]:
    return timegraph_capabilities_payload()


@router.get("/facts")
async def list_timegraph_facts(
    request: Request,
    release_id: str | None = Query(default=None),
    fact_type: str | None = Query(default=None),
    date: str | None = Query(default=None),
    calendar: str | None = Query(default=None),
    source_id: str | None = Query(default=None),
    profile_id: str | None = Query(default=None),
    confidence: str | None = Query(default=None),
    claim_boundary: str | None = Query(default=None),
    jurisdiction: str | None = Query(default=None),
    has_conflicts: bool | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    try:
        return await run_cpu_bound(
            list_facts_payload,
            release_id=release_id,
            fact_type=fact_type,
            date_value=date,
            calendar=calendar,
            source_id=source_id,
            profile_id=profile_id,
            confidence=confidence,
            claim_boundary=claim_boundary,
            jurisdiction=jurisdiction,
            has_conflicts=has_conflicts,
            limit=limit,
            offset=offset,
            trace_id=_trace_id(request),
        )
    except (TimeGraphError, ValueError) as exc:
        _raise_timegraph_error(TimeGraphError(str(exc)))


@router.post("/query")
async def query_timegraph_facts(payload: TimeGraphQuery, request: Request) -> dict[str, Any]:
    try:
        return await run_cpu_bound(query_facts_payload, payload.model_dump(), trace_id=_trace_id(request))
    except (TimeGraphError, ValueError) as exc:
        _raise_timegraph_error(TimeGraphError(str(exc)))


@router.get("/date/{calendar}/{date_value}")
async def get_timegraph_facts_for_date(
    calendar: str,
    date_value: str,
    request: Request,
    release_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=MAX_LIMIT),
) -> dict[str, Any]:
    try:
        return await run_cpu_bound(
            get_facts_for_date_payload,
            calendar,
            date_value,
            release_id=release_id,
            limit=limit,
            trace_id=_trace_id(request),
        )
    except (TimeGraphError, ValueError) as exc:
        _raise_timegraph_error(TimeGraphError(str(exc)))


@router.get("/sources/{source_id}/facts")
async def get_timegraph_facts_for_source(
    source_id: str,
    request: Request,
    release_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=MAX_LIMIT),
) -> dict[str, Any]:
    try:
        return await run_cpu_bound(
            get_facts_for_source_payload,
            source_id,
            release_id=release_id,
            limit=limit,
            trace_id=_trace_id(request),
        )
    except TimeGraphError as exc:
        _raise_timegraph_error(exc)


@router.get("/releases/{release_id}/facts")
async def get_timegraph_facts_for_release(
    release_id: str,
    request: Request,
    limit: int = Query(default=50, ge=1, le=MAX_LIMIT),
) -> dict[str, Any]:
    try:
        return await run_cpu_bound(
            get_facts_for_release_payload,
            release_id,
            limit=limit,
            trace_id=_trace_id(request),
        )
    except (TimeGraphError, TrustInfrastructureError) as exc:
        _raise_timegraph_error(TimeGraphError(str(exc), status_code=getattr(exc, "status_code", 400)))


@router.get("/profiles/{profile_id}/facts")
async def get_timegraph_facts_for_profile(
    profile_id: str,
    request: Request,
    release_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=MAX_LIMIT),
) -> dict[str, Any]:
    try:
        return await run_cpu_bound(
            get_facts_for_profile_payload,
            profile_id,
            release_id=release_id,
            limit=limit,
            trace_id=_trace_id(request),
        )
    except TimeGraphError as exc:
        _raise_timegraph_error(exc)


@router.get("/entities/{entity_id}/relationships")
async def get_timegraph_relationships(
    entity_id: str,
    request: Request,
    release_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=MAX_LIMIT),
) -> dict[str, Any]:
    try:
        return await run_cpu_bound(
            get_relationships_payload,
            entity_id,
            release_id=release_id,
            limit=limit,
            trace_id=_trace_id(request),
        )
    except TimeGraphError as exc:
        _raise_timegraph_error(exc)


@router.get("/facts/{fact_id}/trace")
async def trace_timegraph_fact(
    fact_id: str,
    request: Request,
    release_id: str | None = Query(default=None),
    depth: int = Query(default=2, ge=1, le=5),
) -> dict[str, Any]:
    try:
        return await run_cpu_bound(
            trace_fact_payload,
            fact_id,
            release_id=release_id,
            depth=depth,
            trace_id=_trace_id(request),
        )
    except TimeGraphError as exc:
        _raise_timegraph_error(exc)


@router.get("/facts/{fact_id}")
async def get_timegraph_fact(
    fact_id: str,
    request: Request,
    release_id: str | None = Query(default=None),
) -> dict[str, Any]:
    try:
        return await run_cpu_bound(
            get_fact_payload,
            fact_id,
            release_id=release_id,
            trace_id=_trace_id(request),
        )
    except TimeGraphError as exc:
        _raise_timegraph_error(exc)


@router.get("/conflicts")
async def list_timegraph_conflicts(
    request: Request,
    release_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=MAX_LIMIT),
) -> dict[str, Any]:
    try:
        return await run_cpu_bound(
            list_conflicts_payload,
            release_id=release_id,
            limit=limit,
            trace_id=_trace_id(request),
        )
    except TimeGraphError as exc:
        _raise_timegraph_error(exc)
