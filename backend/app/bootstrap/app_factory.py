"""FastAPI application factory for Project Parva."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse

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
PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESERVED_FRONTEND_PREFIXES = (
    "api",
    "v2",
    "v3",
    "v4",
    "v5",
    "docs",
    "openapi.json",
    "health",
)


def _cors_origins_from_env() -> list[str]:
    raw = os.getenv("CORS_ALLOW_ORIGINS", "").strip()
    if not raw:
        return list(DEFAULT_CORS_ORIGINS)
    origins = [item.strip() for item in raw.split(",") if item.strip()]
    return origins or list(DEFAULT_CORS_ORIGINS)


def _ephemeris_header_value() -> str:
    return get_ephemeris_config().header_value


def _frontend_dist_from_env() -> Path:
    configured = os.getenv("PARVA_FRONTEND_DIST", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return (PROJECT_ROOT / "frontend" / "dist").resolve()


def _is_reserved_frontend_path(path: str) -> bool:
    normalized = path.lstrip("/")
    return any(normalized == prefix or normalized.startswith(f"{prefix}/") for prefix in RESERVED_FRONTEND_PREFIXES)


def create_app() -> FastAPI:
    enable_experimental_api = parse_bool(
        os.getenv("PARVA_ENABLE_EXPERIMENTAL_API"),
        default=False,
    )
    environment = os.getenv("PARVA_ENV", "development")
    serve_frontend = parse_bool(os.getenv("PARVA_SERVE_FRONTEND"), default=False)

    app = FastAPI(
        title="Project Parva API",
        description="Nepal Festival Discovery System",
        version=PRODUCT_VERSION,
    )

    app.state.started_at = datetime.now(timezone.utc)
    app.state.enable_experimental_api = enable_experimental_api
    app.state.environment = environment
    app.state.serve_frontend = serve_frontend

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

    frontend_dist = _frontend_dist_from_env() if serve_frontend else None
    frontend_index = (frontend_dist / "index.html") if frontend_dist else None

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
        if serve_frontend and frontend_index and frontend_index.exists():
            return FileResponse(frontend_index)

        return {
            "name": "Project Parva",
            "description": "Nepal Festival Discovery System",
            "version": PRODUCT_VERSION,
            "public_profile": "v3",
            "experimental_api_enabled": enable_experimental_api,
            "environment": environment,
            "serve_frontend": serve_frontend,
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
            "serve_frontend": serve_frontend,
        }

    if serve_frontend:
        frontend_dist = _frontend_dist_from_env()
        index_file = frontend_dist / "index.html"

        if index_file.exists():

            @app.get("/{full_path:path}", include_in_schema=False)
            async def frontend_spa(full_path: str):
                if _is_reserved_frontend_path(full_path):
                    raise HTTPException(status_code=404, detail="Not Found")

                candidate = (frontend_dist / full_path).resolve()
                if frontend_dist in candidate.parents and candidate.exists() and candidate.is_file():
                    return FileResponse(candidate)

                return FileResponse(index_file)

    return app
