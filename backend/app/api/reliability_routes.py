"""Reliability/SLO endpoints for Year-3 Week 21-24."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.policy import get_policy_metadata
from app.reliability import (
    evaluate_slos,
    get_boundary_suite,
    get_differential_manifest,
    get_runtime_status,
)
from app.reliability.benchmark_manifest import get_benchmark_manifest
from app.reliability.metrics import get_metrics_registry
from app.sources import build_source_review_queue

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
                "doc": "/v3/api/reliability/playbooks",
            },
            {
                "id": "cache_artifact_missing",
                "summary": "Re-run precompute scripts and verify /api/cache/stats.",
                "doc": "/v3/api/reliability/playbooks",
            },
            {
                "id": "source_outage",
                "summary": "Keep engine compute active and flag source_status=stale.",
                "doc": "/v3/api/reliability/playbooks",
            },
        ],
        "policy": get_policy_metadata(),
    }


@router.get("/metrics")
async def reliability_metrics():
    return {
        "runtime": get_runtime_status(),
        "policy": get_policy_metadata(),
    }


@router.get("/metrics.prom", response_class=PlainTextResponse)
async def reliability_metrics_prometheus():
    return get_metrics_registry().to_prometheus()


@router.get("/benchmark-manifest")
async def reliability_benchmark_manifest():
    return {
        "benchmark": get_benchmark_manifest(),
        "policy": get_policy_metadata(),
    }


@router.get("/source-review-queue")
async def reliability_source_review_queue():
    return {
        "queue": build_source_review_queue(),
        "policy": get_policy_metadata(),
    }


@router.get("/boundary-suite")
async def reliability_boundary_suite():
    return {
        "boundary_suite": get_boundary_suite(),
        "policy": get_policy_metadata(),
    }


@router.get("/differential-manifest")
async def reliability_differential_manifest():
    return {
        "differential": get_differential_manifest(),
        "policy": get_policy_metadata(),
    }
