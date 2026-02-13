"""Reliability/SLO endpoints for Year-3 Week 21-24."""

from __future__ import annotations

from fastapi import APIRouter

from app.policy import get_policy_metadata
from app.reliability import evaluate_slos, get_runtime_status


router = APIRouter(prefix="/api/reliability", tags=["reliability"])


@router.get("/status")
async def reliability_status():
    return {
        "runtime": get_runtime_status(),
        "policy": get_policy_metadata(),
    }


@router.get("/slos")
async def reliability_slos():
    return {
        "slo": evaluate_slos(),
        "policy": get_policy_metadata(),
    }


@router.get("/playbooks")
async def reliability_playbooks():
    return {
        "playbooks": [
            {
                "id": "ephemeris_unavailable",
                "summary": "Serve cached/precomputed data and mark responses degraded.",
                "doc": "/docs/RELIABILITY.md#incident-playbooks",
            },
            {
                "id": "cache_artifact_missing",
                "summary": "Re-run precompute scripts and verify /api/cache/stats.",
                "doc": "/docs/RELIABILITY.md#incident-playbooks",
            },
            {
                "id": "source_outage",
                "summary": "Keep engine compute active and flag source_status=stale.",
                "doc": "/docs/RELIABILITY.md#incident-playbooks",
            },
        ],
        "policy": get_policy_metadata(),
    }
