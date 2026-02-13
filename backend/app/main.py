"""
Project Parva - Backend Application
===================================

Festival Discovery API for Nepal.
"""

import json
import os
from typing import Any, Optional

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.responses import JSONResponse
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    calendar_router,
    cache_router,
    explain_router,
    feed_router,
    festival_router,
    forecast_router,
    locations_router,
    observance_router,
    policy_router,
    provenance_router,
    reliability_router,
    webhook_router,
    engine_router,
    resolve_router,
    spec_router,
    integration_feed_router,
)
from app.engine.ephemeris_config import get_ephemeris_config
from app.provenance import get_provenance_payload

PRODUCT_VERSION = "3.0.0"

# Create FastAPI app
app = FastAPI(
    title="Project Parva API",
    description="Nepal Festival Discovery System",
    version=PRODUCT_VERSION,
)

# CORS middleware
# Note: allow_credentials=True requires specific origins, not wildcard
# For development, we allow all origins without credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_REQUEST_BYTES = int(os.getenv("PARVA_MAX_REQUEST_BYTES", "1048576"))  # 1 MB default
MAX_QUERY_LENGTH = int(os.getenv("PARVA_MAX_QUERY_LENGTH", "4096"))
V2_DISABLE_FLAG = "PARVA_DISABLE_V2"


def _score_confidence(level: str) -> float:
    mapping = {
        "official": 1.0,
        "exact": 0.98,
        "computed": 0.9,
        "astronomical": 0.95,
        "estimated": 0.7,
        "unknown": 0.5,
    }
    return mapping.get((level or "unknown").lower(), 0.5)


def _to_v5_confidence_level(level: str) -> str:
    """
    Normalize legacy confidence labels to v5 authority track levels.
    """
    normalized = (level or "unknown").lower()
    if normalized == "official":
        return "official"
    if normalized == "estimated":
        return "estimated"
    if normalized in {"computed", "exact", "astronomical"}:
        return "computed"
    return "unknown"


def _derive_boundary_risk(payload: Any) -> str:
    if not isinstance(payload, dict):
        return "unknown"
    tithi = payload.get("tithi")
    if isinstance(tithi, dict):
        uncertainty = tithi.get("uncertainty")
        if isinstance(uncertainty, dict):
            confidence = uncertainty.get("confidence", "").lower()
            if confidence in {"exact", "high"}:
                return "low"
            if confidence in {"medium", "computed"}:
                return "medium"
            if confidence in {"low", "estimated"}:
                return "high"
    return "unknown"


def _derive_signature(provenance: dict[str, Any]) -> Optional[str]:
    snapshot_id = provenance.get("snapshot_id")
    dataset_hash = provenance.get("dataset_hash")
    rules_hash = provenance.get("rules_hash")
    if not snapshot_id or not dataset_hash or not rules_hash:
        return None
    seed = f"{snapshot_id}:{dataset_hash}:{rules_hash}"
    digest = __import__("hashlib").sha256(seed.encode("utf-8")).hexdigest()
    return f"sha256sig:{digest[:40]}"


def _merge_meta_defaults(defaults: dict[str, Any], provided: dict[str, Any]) -> dict[str, Any]:
    """
    Merge nested metadata dicts while preserving user-provided fields.
    """
    merged: dict[str, Any] = dict(defaults)
    for key, value in provided.items():
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, dict)
        ):
            merged[key] = _merge_meta_defaults(merged[key], value)
        else:
            merged[key] = value
    return merged


def _extract_meta(payload: Any, *, track: str = "v4") -> dict[str, Any]:
    """Build v4 envelope metadata from legacy v2/v3 payloads."""
    if not isinstance(payload, dict):
        return {
            "confidence": "computed",
            "method": "unknown",
            "provenance": {},
            "uncertainty": {"level": "unknown", "interval_hours": None},
            "trace_id": None,
        }

    tithi_block = payload.get("tithi") if isinstance(payload.get("tithi"), dict) else {}
    bs_block = payload.get("bikram_sambat") if isinstance(payload.get("bikram_sambat"), dict) else {}

    confidence_level_raw = (
        payload.get("confidence")
        or tithi_block.get("confidence")
        or bs_block.get("confidence")
        or payload.get("panchanga", {}).get("confidence")
        or "unknown"
    )
    confidence_level = str(confidence_level_raw).lower()
    method = payload.get("method") or tithi_block.get("method") or payload.get("engine_version") or "unknown"

    verify_url = "/v5/api/provenance/root" if track == "v5" else "/v4/api/provenance/root"
    fallback_provenance = get_provenance_payload(
        verify_url=verify_url,
        create_if_missing=True,
    )
    raw_provenance = payload.get("provenance") if isinstance(payload.get("provenance"), dict) else {}
    provenance = _merge_meta_defaults(fallback_provenance, raw_provenance)

    signature = _derive_signature(provenance)
    if "signature" not in provenance:
        provenance = {**provenance, "signature": signature}
    uncertainty = payload.get("uncertainty")
    if not isinstance(uncertainty, dict):
        uncertainty = {"interval_hours": None, "boundary_risk": _derive_boundary_risk(payload)}

    trace_id = (
        payload.get("calculation_trace_id")
        or payload.get("trace_id")
        or (payload.get("trace", {}).get("trace_id") if isinstance(payload.get("trace"), dict) else None)
    )
    if track == "v5":
        v5_confidence_level = _to_v5_confidence_level(confidence_level)
        confidence = {
            "level": v5_confidence_level,
            "score": _score_confidence(v5_confidence_level),
        }
        return {
            "confidence": confidence,
            "method": method,
            "provenance": provenance,
            "uncertainty": {
                "interval_hours": uncertainty.get("interval_hours"),
                "boundary_risk": uncertainty.get("boundary_risk", _derive_boundary_risk(payload)),
            },
            "trace_id": trace_id,
            "policy": {
                "profile": "np-mainstream",
                "jurisdiction": "NP",
                "advisory": True,
            },
        }

    return {
        "confidence": confidence_level,
        "method": method,
        "provenance": provenance,
        "uncertainty": uncertainty,
        "trace_id": trace_id,
    }


@app.middleware("http")
async def request_size_guard(request: Request, call_next):
    """
    Basic abuse guardrails:
    - Reject very large bodies
    - Reject unusually long query strings
    """
    if len(request.url.query) > MAX_QUERY_LENGTH:
        return JSONResponse(
            status_code=414,
            content={"detail": "Query string too long"},
        )

    cl = request.headers.get("content-length")
    if cl:
        try:
            if int(cl) > MAX_REQUEST_BYTES:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request payload too large"},
                )
        except ValueError:
            # Malformed content-length header
            return JSONResponse(status_code=400, content={"detail": "Invalid content-length header"})

    return await call_next(request)


@app.middleware("http")
async def version_gate(request: Request, call_next):
    """
    Optional migration gate for v2 endpoints.
    When PARVA_DISABLE_V2=true, v2 API paths return 410 Gone with migration hint.
    """
    disable_v2 = os.getenv(V2_DISABLE_FLAG, "false").strip().lower() in {"1", "true", "yes"}
    if disable_v2 and request.url.path.startswith("/v2/api/"):
        return JSONResponse(
            status_code=410,
            content={
                "detail": "v2 API is deprecated. Please migrate to /v3/api endpoints.",
                "migration_guide": "/docs/MIGRATION_V2_V3.md",
                "successor_version": "/v3/docs",
            },
        )
    return await call_next(request)


@app.middleware("http")
async def v4_envelope_adapter(request: Request, call_next):
    """
    Normalize v4 API responses to canonical envelope shape:
    { "data": ..., "meta": ... }.
    """
    response = await call_next(request)
    is_v4 = request.url.path.startswith("/v4/api/")
    is_v5 = request.url.path.startswith("/v5/api/")
    if not (is_v4 or is_v5):
        return response
    if response.status_code >= 400:
        return response

    content_type = response.headers.get("content-type", "").lower()
    if "application/json" not in content_type:
        return response

    body = b""
    async for chunk in response.body_iterator:
        body += chunk

    if not body:
        return response

    try:
        payload = json.loads(body)
    except Exception:
        headers = dict(response.headers)
        headers.pop("content-length", None)
        return Response(
            content=body,
            status_code=response.status_code,
            media_type=response.media_type,
            headers=headers,
        )

    if isinstance(payload, dict) and "data" in payload and "meta" in payload:
        track = "v5" if is_v5 else "v4"
        existing_meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
        default_meta = _extract_meta(payload.get("data"), track=track)
        merged_meta = _merge_meta_defaults(default_meta, existing_meta)
        envelope = {
            "data": payload.get("data"),
            "meta": merged_meta,
        }
    else:
        track = "v5" if is_v5 else "v4"
        envelope = {
            "data": payload,
            "meta": _extract_meta(payload, track=track),
        }

    headers = dict(response.headers)
    headers.pop("content-length", None)
    return JSONResponse(
        status_code=response.status_code,
        content=envelope,
        headers=headers,
    )


@app.middleware("http")
async def add_engine_headers(request: Request, call_next):
    """
    Add response-level engine metadata so all clients can trace calculation mode.
    """
    response = await call_next(request)
    cfg = get_ephemeris_config()
    response.headers["X-Parva-Ephemeris"] = cfg.header_value
    if request.url.path.startswith("/v4/"):
        response.headers["X-Parva-Engine"] = "v4"
    elif request.url.path.startswith("/v5/"):
        response.headers["X-Parva-Engine"] = "v5"
    elif request.url.path.startswith("/v3/"):
        response.headers["X-Parva-Engine"] = "v3"
    else:
        response.headers["X-Parva-Engine"] = "v2"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    # Deprecation headers for unversioned API routes.
    if request.url.path.startswith("/api/"):
        response.headers["Deprecation"] = "true"
        response.headers["Sunset"] = "Thu, 01 May 2027 00:00:00 GMT"
        response.headers["Link"] = f'<{request.url_for("v2_docs")}>; rel="successor-version"'
    if request.url.path.startswith("/v2/api/"):
        response.headers["Deprecation"] = "true"
        response.headers["Sunset"] = "Wed, 01 Jan 2029 00:00:00 GMT"
        response.headers["Link"] = f'<{request.url_for("v3_docs")}>; rel="successor-version"'
    return response


# Include routers
app.include_router(festival_router)
app.include_router(calendar_router)
app.include_router(cache_router)
app.include_router(explain_router)
app.include_router(locations_router)
app.include_router(observance_router)
app.include_router(policy_router)
app.include_router(feed_router)
app.include_router(webhook_router)
app.include_router(provenance_router)
app.include_router(reliability_router)
app.include_router(engine_router)
app.include_router(forecast_router)
app.include_router(resolve_router)
app.include_router(spec_router)
app.include_router(integration_feed_router)

# Versioned v2 aliases
app.include_router(festival_router, prefix="/v2")
app.include_router(calendar_router, prefix="/v2")
app.include_router(cache_router, prefix="/v2")
app.include_router(explain_router, prefix="/v2")
app.include_router(locations_router, prefix="/v2")
app.include_router(observance_router, prefix="/v2")
app.include_router(policy_router, prefix="/v2")
app.include_router(feed_router, prefix="/v2")
app.include_router(webhook_router, prefix="/v2")
app.include_router(provenance_router, prefix="/v2")
app.include_router(reliability_router, prefix="/v2")
app.include_router(engine_router, prefix="/v2")
app.include_router(forecast_router, prefix="/v2")
app.include_router(resolve_router, prefix="/v2")
app.include_router(spec_router, prefix="/v2")
app.include_router(integration_feed_router, prefix="/v2")

# Versioned v3 aliases (LTS track)
app.include_router(festival_router, prefix="/v3")
app.include_router(calendar_router, prefix="/v3")
app.include_router(cache_router, prefix="/v3")
app.include_router(explain_router, prefix="/v3")
app.include_router(locations_router, prefix="/v3")
app.include_router(observance_router, prefix="/v3")
app.include_router(policy_router, prefix="/v3")
app.include_router(feed_router, prefix="/v3")
app.include_router(webhook_router, prefix="/v3")
app.include_router(provenance_router, prefix="/v3")
app.include_router(reliability_router, prefix="/v3")
app.include_router(engine_router, prefix="/v3")
app.include_router(forecast_router, prefix="/v3")
app.include_router(resolve_router, prefix="/v3")
app.include_router(spec_router, prefix="/v3")
app.include_router(integration_feed_router, prefix="/v3")

# Versioned v4 aliases (normalized contract track)
app.include_router(festival_router, prefix="/v4")
app.include_router(calendar_router, prefix="/v4")
app.include_router(cache_router, prefix="/v4")
app.include_router(explain_router, prefix="/v4")
app.include_router(locations_router, prefix="/v4")
app.include_router(observance_router, prefix="/v4")
app.include_router(policy_router, prefix="/v4")
app.include_router(feed_router, prefix="/v4")
app.include_router(webhook_router, prefix="/v4")
app.include_router(provenance_router, prefix="/v4")
app.include_router(reliability_router, prefix="/v4")
app.include_router(engine_router, prefix="/v4")
app.include_router(forecast_router, prefix="/v4")
app.include_router(resolve_router, prefix="/v4")
app.include_router(spec_router, prefix="/v4")
app.include_router(integration_feed_router, prefix="/v4")

# Versioned v5 aliases (authority track)
app.include_router(festival_router, prefix="/v5")
app.include_router(calendar_router, prefix="/v5")
app.include_router(cache_router, prefix="/v5")
app.include_router(explain_router, prefix="/v5")
app.include_router(locations_router, prefix="/v5")
app.include_router(observance_router, prefix="/v5")
app.include_router(policy_router, prefix="/v5")
app.include_router(feed_router, prefix="/v5")
app.include_router(webhook_router, prefix="/v5")
app.include_router(provenance_router, prefix="/v5")
app.include_router(reliability_router, prefix="/v5")
app.include_router(engine_router, prefix="/v5")
app.include_router(forecast_router, prefix="/v5")
app.include_router(resolve_router, prefix="/v5")
app.include_router(spec_router, prefix="/v5")
app.include_router(integration_feed_router, prefix="/v5")


@app.get("/v2/openapi.json")
async def v2_openapi():
    """
    Versioned OpenAPI schema endpoint.
    """
    return app.openapi()


@app.get("/v2/docs", name="v2_docs")
async def v2_docs():
    """
    Versioned docs entrypoint.
    """
    return RedirectResponse(url="/docs")


@app.get("/v3/openapi.json")
async def v3_openapi():
    """
    Versioned OpenAPI schema endpoint for v3.
    """
    return app.openapi()


@app.get("/v3/docs", name="v3_docs")
async def v3_docs():
    """
    Versioned docs entrypoint for v3.
    """
    return RedirectResponse(url="/docs")


@app.get("/v4/openapi.json")
async def v4_openapi():
    """
    Versioned OpenAPI schema endpoint for v4.
    """
    return app.openapi()


@app.get("/v4/docs", name="v4_docs")
async def v4_docs():
    """
    Versioned docs entrypoint for v4.
    """
    return RedirectResponse(url="/docs")


@app.get("/v5/openapi.json")
async def v5_openapi():
    """
    Versioned OpenAPI schema endpoint for v5.
    """
    return app.openapi()


@app.get("/v5/docs", name="v5_docs")
async def v5_docs():
    """
    Versioned docs entrypoint for v5.
    """
    return RedirectResponse(url="/docs")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Project Parva",
        "description": "Nepal Festival Discovery System",
        "version": PRODUCT_VERSION,
        "endpoints": {
            "festivals": "/api/festivals",
            "festivals_v2": "/v2/api/festivals",
            "festivals_v3": "/v3/api/festivals",
            "festivals_v4": "/v4/api/festivals",
            "festivals_v5": "/v5/api/festivals",
            "observances_v2": "/v2/api/observances",
            "observances_v3": "/v3/api/observances",
            "observances_v4": "/v4/api/observances",
            "observances_v5": "/v5/api/observances",
            "feeds_v2": "/v2/api/feeds/ical",
            "feeds_v3": "/v3/api/feeds/ical",
            "feeds_v4": "/v4/api/feeds/ical",
            "feeds_v5": "/v5/api/feeds/ical",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
