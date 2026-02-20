"""FastAPI application factory for Project Parva."""

from __future__ import annotations

import os
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.bootstrap.middleware import (
    build_engine_headers,
    build_envelope_adapter,
    build_experimental_version_gate,
    build_request_size_guard,
    parse_bool,
)
from app.bootstrap.router_registry import register_routers
from app.engine.ephemeris_config import get_ephemeris_config

PRODUCT_VERSION = "3.0.0"
DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]


def _cors_origins_from_env() -> list[str]:
    raw = os.getenv("CORS_ALLOW_ORIGINS", "").strip()
    if not raw:
        return list(DEFAULT_CORS_ORIGINS)
    origins = [item.strip() for item in raw.split(",") if item.strip()]
    return origins or list(DEFAULT_CORS_ORIGINS)


def _ephemeris_header_value() -> str:
    return get_ephemeris_config().header_value


def create_app() -> FastAPI:
    enable_experimental_api = parse_bool(
        os.getenv("PARVA_ENABLE_EXPERIMENTAL_API"),
        default=False,
    )
    environment = os.getenv("PARVA_ENV", "development")

    app = FastAPI(
        title="Project Parva API",
        description="Nepal Festival Discovery System",
        version=PRODUCT_VERSION,
    )

    app.state.started_at = datetime.now(timezone.utc)
    app.state.enable_experimental_api = enable_experimental_api
    app.state.environment = environment

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins_from_env(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    max_request_bytes = int(os.getenv("PARVA_MAX_REQUEST_BYTES", "1048576"))
    max_query_length = int(os.getenv("PARVA_MAX_QUERY_LENGTH", "4096"))

    app.middleware("http")(
        build_request_size_guard(
            max_query_length=max_query_length,
            max_request_bytes=max_request_bytes,
        )
    )
    app.middleware("http")(
        build_experimental_version_gate(enable_experimental_api=enable_experimental_api)
    )
    app.middleware("http")(
        build_envelope_adapter(enable_experimental_api=enable_experimental_api)
    )
    app.middleware("http")(
        build_engine_headers(
            ephemeris_header_value=_ephemeris_header_value,
            enable_experimental_api=enable_experimental_api,
        )
    )

    register_routers(
        app,
        enable_experimental_api=enable_experimental_api,
        environment=environment,
    )

    @app.get("/v3/openapi.json")
    async def v3_openapi():
        return app.openapi()

    @app.get("/v3/docs", name="v3_docs")
    async def v3_docs():
        return RedirectResponse(url="/docs")

    if enable_experimental_api:
        @app.get("/v2/openapi.json")
        async def v2_openapi():
            return app.openapi()

        @app.get("/v2/docs", name="v2_docs")
        async def v2_docs():
            return RedirectResponse(url="/docs")

        @app.get("/v4/openapi.json")
        async def v4_openapi():
            return app.openapi()

        @app.get("/v4/docs", name="v4_docs")
        async def v4_docs():
            return RedirectResponse(url="/docs")

        @app.get("/v5/openapi.json")
        async def v5_openapi():
            return app.openapi()

        @app.get("/v5/docs", name="v5_docs")
        async def v5_docs():
            return RedirectResponse(url="/docs")

    @app.get("/")
    async def root():
        return {
            "name": "Project Parva",
            "description": "Nepal Festival Discovery System",
            "version": PRODUCT_VERSION,
            "public_profile": "v3",
            "experimental_api_enabled": enable_experimental_api,
            "environment": environment,
            "endpoints": {
                "festivals": "/v3/api/festivals",
                "calendar_today": "/v3/api/calendar/today",
                "panchanga": "/v3/api/calendar/panchanga?date=2026-02-15",
                "feeds": "/v3/api/feeds/all.ics",
                "docs": "/docs",
            },
        }

    @app.get("/health")
    async def health():
        now = datetime.now(timezone.utc)
        uptime_seconds = int((now - app.state.started_at).total_seconds())
        return {
            "status": "healthy",
            "version": PRODUCT_VERSION,
            "uptime_seconds": uptime_seconds,
            "public_profile": "v3",
            "experimental_api_enabled": enable_experimental_api,
            "environment": environment,
        }

    return app
