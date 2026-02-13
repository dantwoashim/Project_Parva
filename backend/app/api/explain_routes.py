"""Explainability trace retrieval routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.explainability import get_reason_trace, list_recent_traces
from app.policy import get_policy_metadata


router = APIRouter(prefix="/api/explain", tags=["explainability"])


@router.get("/{trace_id}")
async def get_trace(trace_id: str):
    payload = get_reason_trace(trace_id)
    if not payload:
        raise HTTPException(status_code=404, detail=f"Trace not found: {trace_id}")
    payload["policy"] = get_policy_metadata()
    return payload


@router.get("")
@router.get("/")
async def list_traces(limit: int = Query(20, ge=1, le=200)):
    return {
        "count": limit,
        "traces": list_recent_traces(limit=limit),
        "policy": get_policy_metadata(),
    }
