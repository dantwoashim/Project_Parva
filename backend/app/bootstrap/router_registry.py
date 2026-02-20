"""Router registration for public and experimental API profiles."""

from __future__ import annotations

from fastapi import FastAPI

from app.api import (
    cache_router,
    calendar_router,
    engine_router,
    explain_router,
    feed_router,
    festival_router,
    forecast_router,
    integration_feed_router,
    locations_router,
    muhurta_router,
    observance_router,
    personal_router,
    policy_router,
    provenance_router,
    public_artifacts_router,
    reliability_router,
    resolve_router,
    spec_router,
    webhook_router,
    kundali_router,
)

PUBLIC_ROUTERS = [
    festival_router,
    calendar_router,
    cache_router,
    explain_router,
    locations_router,
    observance_router,
    policy_router,
    feed_router,
    webhook_router,
    engine_router,
    forecast_router,
    resolve_router,
    integration_feed_router,
    personal_router,
    muhurta_router,
    kundali_router,
]

TRUST_ROUTERS = [
    provenance_router,
    reliability_router,
    spec_router,
    public_artifacts_router,
]


DEV_ENV_VALUES = {"dev", "development", "local", "test"}


def _is_dev_environment(environment: str) -> bool:
    return environment.strip().lower() in DEV_ENV_VALUES


def register_routers(
    app: FastAPI,
    *,
    enable_experimental_api: bool,
    environment: str = "development",
) -> None:
    """Register /api + /v3 routers, with optional experimental version tracks."""
    include_trust = _is_dev_environment(environment) or enable_experimental_api
    routers = [*PUBLIC_ROUTERS, *(TRUST_ROUTERS if include_trust else [])]

    for router in routers:
        app.include_router(router)

    for router in routers:
        app.include_router(router, prefix="/v3")

    if enable_experimental_api:
        for prefix in ("/v2", "/v4", "/v5"):
            for router in routers:
                app.include_router(router, prefix=prefix)
