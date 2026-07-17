"""FastAPI application factory for Project Parva."""

from __future__ import annotations

import logging
import time
from datetime import date, datetime, timezone
from importlib import metadata
from json import JSONDecodeError
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

from app.bootstrap.access_control import find_unclassified_api_routes
from app.bootstrap.middleware import (
    ExperimentalEnvelopeMiddleware,
    RequestSizeGuardMiddleware,
    build_access_control_guard,
    build_engine_headers,
    build_experimental_version_gate,
    build_rate_limit_guard,
    build_request_context,
)
from app.bootstrap.rate_limit import create_rate_limiter_backend
from app.bootstrap.router_registry import register_routers
from app.bootstrap.settings import load_settings, validate_settings
from app.cache.precomputed import get_cache_stats, prewarm_hot_set
from app.core.errors import build_error_payload
from app.engine.ephemeris_config import get_ephemeris_config
from app.festivals.repository import validate_festival_catalog
from app.festivals.use_cases import upcoming_festivals_payload
from app.policy import get_route_access_manifest

try:
    PRODUCT_VERSION = metadata.version("project-parva")
except metadata.PackageNotFoundError:  # pragma: no cover - source checkout without install.
    PRODUCT_VERSION = "0+local"
logger = logging.getLogger(__name__)
DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]
DEFAULT_CORS_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
DEFAULT_CORS_HEADERS = [
    "Authorization",
    "Content-Type",
    "X-API-Key",
    "X-Parva-Envelope",
    "X-Request-ID",
]
DEPLOYED_ENVIRONMENTS = {"production", "staging"}
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
IMMUTABLE_FRONTEND_PREFIXES = (
    "assets/",
    "festival-images/",
    "front-end-images/",
    "payment-qr/",
)


def _frontend_response(path, *, immutable: bool = False) -> FileResponse:
    response = FileResponse(path)
    response.headers["Cache-Control"] = (
        "public, max-age=31536000, immutable" if immutable else "no-cache"
    )
    return response


def _is_immutable_frontend_asset(path: str) -> bool:
    normalized = path.lstrip("/")
    return any(normalized.startswith(prefix) for prefix in IMMUTABLE_FRONTEND_PREFIXES)


def _cors_origins_from_env() -> list[str]:
    import os

    raw = os.getenv("CORS_ALLOW_ORIGINS", "").strip() or os.getenv("PARVA_CORS_ORIGINS", "").strip()
    if not raw:
        return list(DEFAULT_CORS_ORIGINS)
    origins = [item.strip() for item in raw.split(",") if item.strip()]
    return origins or list(DEFAULT_CORS_ORIGINS)


def _ephemeris_header_value() -> str:
    return get_ephemeris_config().header_value


def _is_reserved_frontend_path(path: str) -> bool:
    normalized = path.lstrip("/")
    return any(
        normalized == prefix or normalized.startswith(f"{prefix}/")
        for prefix in RESERVED_FRONTEND_PREFIXES
    )


def _build_startup_checks(settings) -> dict[str, Any]:
    cache_stats = get_cache_stats()
    frontend_index = settings.frontend_dist / "index.html"
    try:
        festival_catalog = validate_festival_catalog()
        festival_catalog_check = {
            "required": True,
            "ok": True,
            "detail": festival_catalog,
        }
    except (FileNotFoundError, JSONDecodeError, OSError, TypeError, UnicodeDecodeError, ValueError) as exc:
        festival_catalog_check = {
            "required": True,
            "ok": False,
            "detail": str(exc),
        }

    checks = {
        "config": {"required": True, "ok": True, "detail": "validated"},
        "festival_catalog": festival_catalog_check,
        "source_code": {
            "required": settings.environment.lower() == "production",
            "ok": bool(settings.source_url),
            "detail": settings.source_url
            or "Set PARVA_SOURCE_URL to a public repository or source archive.",
        },
        "precomputed": {
            "required": settings.require_precomputed,
            "ok": cache_stats.get("file_count", 0) > 0,
            "detail": cache_stats,
        },
        "frontend_dist": {
            "required": settings.serve_frontend and settings.environment.lower() == "production",
            "ok": frontend_index.exists(),
            "path": str(frontend_index),
        },
    }
    ready = all((not item["required"]) or item["ok"] for item in checks.values())
    return {
        "completed": True,
        "ready": ready,
        "checks": checks,
    }


def _service_metadata(settings) -> dict[str, object]:
    return {
        "license": settings.license_mode,
        "source_code_url": settings.source_url,
    }


def _validate_startup(settings) -> tuple[dict[str, Any], object]:
    validation_errors = validate_settings(settings)
    if validation_errors:
        raise RuntimeError("Startup validation failed: " + " ".join(validation_errors))

    startup_checks = _build_startup_checks(settings)
    if not startup_checks["checks"]["festival_catalog"]["ok"]:
        detail = startup_checks["checks"]["festival_catalog"]["detail"]
        raise RuntimeError(f"Startup validation failed: {detail}")
    if settings.require_precomputed and not startup_checks["checks"]["precomputed"]["ok"]:
        raise RuntimeError(
            "Startup validation failed: production profile requires precomputed artifacts. "
            "Run the precompute pipeline or set PARVA_REQUIRE_PRECOMPUTED=false explicitly."
        )

    rate_limit_backend = create_rate_limiter_backend(
        backend_name=settings.rate_limit_backend,
        redis_url=settings.redis_url,
        memory_max_buckets=settings.rate_limit_max_buckets,
    )
    return startup_checks, rate_limit_backend


def _initialize_app_state(app: FastAPI, settings, startup_checks: dict[str, object]) -> None:
    app.state.started_at = datetime.now(timezone.utc)
    app.state.enable_experimental_api = settings.enable_experimental_api
    app.state.enable_research_api = settings.enable_research_api
    app.state.environment = settings.environment
    app.state.route_profile = settings.route_profile
    app.state.license_mode = settings.license_mode
    app.state.serve_frontend = settings.serve_frontend
    app.state.rate_limit_backend = settings.rate_limit_backend
    app.state.source_url = settings.source_url
    app.state.settings = settings
    app.state.startup_checks = startup_checks
    app.state.prewarm = None


def _install_middleware(app: FastAPI, settings, rate_limit_backend) -> None:
    cors_origins = _cors_origins_from_env()
    if settings.environment.strip().lower() in DEPLOYED_ENVIRONMENTS:
        localhost_origins = [
            origin
            for origin in cors_origins
            if "localhost" in origin or "127.0.0.1" in origin
        ]
        if localhost_origins:
            raise RuntimeError(
                "Startup validation failed: production or staging CORS origins cannot include localhost."
            )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=DEFAULT_CORS_METHODS,
        allow_headers=DEFAULT_CORS_HEADERS,
    )

    app.middleware("http")(
        build_engine_headers(
            ephemeris_header_value=_ephemeris_header_value,
            license_mode=settings.license_mode,
            source_url=settings.source_url,
            enable_experimental_api=settings.enable_experimental_api,
        )
    )
    app.add_middleware(
        ExperimentalEnvelopeMiddleware,
        enable_experimental_api=settings.enable_experimental_api,
    )
    app.middleware("http")(build_rate_limit_guard(settings=settings, backend=rate_limit_backend))
    app.middleware("http")(build_access_control_guard(settings=settings))
    app.middleware("http")(
        build_experimental_version_gate(enable_experimental_api=settings.enable_experimental_api)
    )
    app.add_middleware(
        RequestSizeGuardMiddleware,
        max_query_length=settings.max_query_length,
        max_request_bytes=settings.max_request_bytes,
    )
    app.middleware("http")(
        build_request_context(product_version=PRODUCT_VERSION, settings=settings)
    )


def _request_id_for_error(request) -> str:
    request_id = getattr(request.state, "request_id", None)
    return str(request_id) if request_id else "unknown"


def _register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException):
        request_id = _request_id_for_error(request)
        return JSONResponse(
            status_code=exc.status_code,
            headers=exc.headers,
            content=build_error_payload(
                status_code=exc.status_code,
                detail=exc.detail,
                request_id=request_id,
                version=PRODUCT_VERSION,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc: RequestValidationError):
        request_id = _request_id_for_error(request)
        errors = jsonable_encoder(exc.errors())
        return JSONResponse(
            status_code=422,
            content=build_error_payload(
                status_code=422,
                detail="Request validation failed",
                request_id=request_id,
                version=PRODUCT_VERSION,
                details={"errors": errors},
                extra={"errors": errors},
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request, exc: Exception):
        logger.exception(
            "Unhandled exception for %s %s request_id=%s",
            getattr(request, "method", "UNKNOWN"),
            getattr(getattr(request, "url", None), "path", "unknown"),
            _request_id_for_error(request),
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content=build_error_payload(
                status_code=500,
                detail="Internal Server Error",
                request_id=_request_id_for_error(request),
                version=PRODUCT_VERSION,
            ),
        )


def _register_version_docs_routes(app: FastAPI, *, enable_experimental_api: bool) -> None:
    @app.get("/v3/openapi.json")
    async def v3_openapi():
        return app.openapi()

    @app.get("/v3/docs", name="v3_docs")
    async def v3_docs():
        return RedirectResponse(url="/docs")

    if not enable_experimental_api:
        return

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


def _register_source_route(app: FastAPI, settings) -> None:
    @app.get("/source", include_in_schema=False)
    async def source_code():
        if settings.source_url:
            return RedirectResponse(url=settings.source_url)
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Source publication URL is not configured. Set PARVA_SOURCE_URL.",
                **_service_metadata(settings),
            },
        )


def _register_root_and_health_routes(app: FastAPI, settings) -> None:
    frontend_dist = settings.frontend_dist if settings.serve_frontend else None
    frontend_index = (frontend_dist / "index.html") if frontend_dist else None

    @app.get("/")
    async def root():
        if settings.serve_frontend and frontend_index and frontend_index.exists():
            return _frontend_response(frontend_index)

        return {
            "name": "Project Parva",
            "description": "Nepal Festival Discovery System",
            "version": PRODUCT_VERSION,
            **_service_metadata(settings),
            "public_profile": "v3",
            "experimental_api_enabled": settings.enable_experimental_api,
            "environment": settings.environment,
            "serve_frontend": settings.serve_frontend,
            "access_model": {
                "name": "public_compute_with_admin_mutations",
                "policy_url": "/v3/api/policy",
            },
            "route_access": get_route_access_manifest(),
            "endpoints": {
                "festivals": "/v3/api/festivals",
                "calendar_today": "/v3/api/calendar/today",
                "panchanga": "/v3/api/calendar/panchanga?date=2026-02-15",
                "feeds": "/v3/api/feeds/all.ics",
                "docs": "/docs",
                "source": "/source",
            },
        }

    @app.get("/health")
    async def health():
        now = datetime.now(timezone.utc)
        uptime_seconds = int((now - app.state.started_at).total_seconds())
        return {
            "status": "healthy" if app.state.startup_checks.get("ready") else "degraded",
            "version": PRODUCT_VERSION,
            **_service_metadata(settings),
            "uptime_seconds": uptime_seconds,
            "public_profile": "v3",
            "experimental_api_enabled": settings.enable_experimental_api,
            "environment": settings.environment,
            "serve_frontend": settings.serve_frontend,
            "startup": app.state.startup_checks,
            "prewarm": app.state.prewarm,
        }

    @app.get("/health/live")
    async def health_live():
        return {
            "status": "alive",
            "version": PRODUCT_VERSION,
        }

    @app.get("/health/startup")
    async def health_startup():
        status_code = 200 if app.state.startup_checks.get("completed") else 503
        return JSONResponse(status_code=status_code, content=app.state.startup_checks)

    @app.get("/health/ready")
    async def health_ready():
        payload = {
            "status": "ready" if app.state.startup_checks.get("ready") else "not_ready",
            "version": PRODUCT_VERSION,
            **_service_metadata(settings),
            "checks": app.state.startup_checks.get("checks", {}),
            "prewarm": app.state.prewarm,
        }
        return JSONResponse(
            status_code=200 if app.state.startup_checks.get("ready") else 503, content=payload
        )


def _register_frontend_spa_route(app: FastAPI, settings) -> None:
    if not settings.serve_frontend:
        return

    frontend_dist = settings.frontend_dist
    index_file = frontend_dist / "index.html"
    if not index_file.exists():
        return

    @app.get("/{full_path:path}", include_in_schema=False)
    async def frontend_spa(full_path: str):
        if _is_reserved_frontend_path(full_path):
            raise HTTPException(status_code=404, detail="Not Found")

        candidate = (frontend_dist / full_path).resolve()
        if frontend_dist in candidate.parents and candidate.exists() and candidate.is_file():
            return _frontend_response(candidate, immutable=_is_immutable_frontend_asset(full_path))

        return _frontend_response(index_file)


def _prewarm_runtime_hotset(app: FastAPI, settings) -> None:
    if not settings.prewarm_hotset:
        return
    prewarm: dict[str, Any] = {}
    try:
        prewarm["precomputed"] = prewarm_hot_set()
    except (OSError, TypeError, ValueError) as exc:
        logger.warning("Precomputed hot-set prewarm failed: %s", exc)
        prewarm["precomputed"] = {"status": "failed", "detail": str(exc)}

    festival_start = time.perf_counter()
    try:
        festival_payload = upcoming_festivals_payload(
            days=30,
            from_date=date.today(),
            quality_band="all",
            profile=None,
        )
        prewarm["festival_upcoming"] = {
            "status": "ok",
            "days": 30,
            "festival_count": len(festival_payload.festivals),
            "elapsed_ms": round((time.perf_counter() - festival_start) * 1000.0, 3),
        }
    except (OSError, TypeError, ValueError) as exc:
        logger.warning("Festival upcoming prewarm failed: %s", exc)
        prewarm["festival_upcoming"] = {"status": "failed", "detail": str(exc)}

    app.state.prewarm = prewarm


def create_app() -> FastAPI:
    settings = load_settings()
    startup_checks, rate_limit_backend = _validate_startup(settings)

    app = FastAPI(
        title="Project Parva API",
        description="Nepal Festival Discovery System",
        version=PRODUCT_VERSION,
    )
    _initialize_app_state(app, settings, startup_checks)
    _install_middleware(app, settings, rate_limit_backend)
    _register_exception_handlers(app)
    register_routers(
        app,
        enable_experimental_api=settings.enable_experimental_api,
        enable_research_api=settings.enable_research_api,
        show_private_schema=settings.show_private_schema,
        environment=settings.environment,
        route_profile=settings.route_profile,
    )
    unclassified_routes = find_unclassified_api_routes(app.routes)
    if unclassified_routes:
        rendered = ", ".join(unclassified_routes[:10])
        suffix = " ..." if len(unclassified_routes) > 10 else ""
        raise RuntimeError(
            "Startup validation failed: unclassified API routes detected: " f"{rendered}{suffix}"
        )
    _register_version_docs_routes(app, enable_experimental_api=settings.enable_experimental_api)
    _register_source_route(app, settings)
    _register_root_and_health_routes(app, settings)
    _register_frontend_spa_route(app, settings)
    _prewarm_runtime_hotset(app, settings)
    return app
