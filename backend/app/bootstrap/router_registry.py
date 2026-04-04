"""Router registration for public and experimental API profiles."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import APIRouter, FastAPI

from app.api import (
    cache_router,
    calendar_router,
    engine_router,
    explain_router,
    feed_router,
    festival_router,
    festival_timeline_router,
    forecast_router,
    glossary_router,
    integration_feed_router,
    kundali_graph_router,
    kundali_router,
    locations_router,
    muhurta_calendar_router,
    muhurta_heatmap_router,
    muhurta_router,
    observance_router,
    personal_router,
    place_router,
    policy_router,
    provenance_router,
    public_artifacts_router,
    reliability_router,
    resolve_router,
    spec_router,
    temporal_compass_router,
)

@dataclass(frozen=True)
class RouterRegistration:
    router: APIRouter
    audience: str
    access_policy: str
    policy_name: str
    policy_path: str | None = None


ROUTER_REGISTRATIONS = [
    # Keep timeline router before dynamic /festivals/{festival_id} routes.
    RouterRegistration(festival_timeline_router, "public", "public", "festivals_timeline"),
    RouterRegistration(festival_router, "public", "public", "festivals"),
    RouterRegistration(calendar_router, "public", "public", "calendar"),
    RouterRegistration(cache_router, "public", "public", "cache"),
    RouterRegistration(explain_router, "public", "public", "explain"),
    RouterRegistration(locations_router, "public", "public", "locations"),
    RouterRegistration(observance_router, "public", "public", "observances"),
    RouterRegistration(place_router, "public", "public", "places"),
    RouterRegistration(policy_router, "public", "public", "policy"),
    RouterRegistration(feed_router, "public", "public", "feeds"),
    RouterRegistration(engine_router, "public", "public", "engine"),
    RouterRegistration(forecast_router, "public", "public", "forecast"),
    RouterRegistration(resolve_router, "public", "public", "resolve", policy_path="/api/resolve"),
    RouterRegistration(integration_feed_router, "public", "public", "integrations_feeds"),
    RouterRegistration(personal_router, "public", "public", "personal"),
    RouterRegistration(muhurta_router, "public", "public", "muhurta"),
    RouterRegistration(muhurta_calendar_router, "public", "public", "muhurta_calendar"),
    RouterRegistration(kundali_router, "public", "public", "kundali"),
    RouterRegistration(temporal_compass_router, "public", "public", "temporal"),
    RouterRegistration(muhurta_heatmap_router, "public", "public", "muhurta_heatmap"),
    RouterRegistration(kundali_graph_router, "public", "public", "kundali_graph"),
    RouterRegistration(glossary_router, "public", "public", "glossary"),
    RouterRegistration(provenance_router, "trust", "provenance", "provenance"),
    RouterRegistration(reliability_router, "trust", "reliability_read", "reliability"),
    RouterRegistration(spec_router, "trust", "spec_read", "spec"),
    RouterRegistration(public_artifacts_router, "trust", "public_artifacts_read", "public_artifacts"),
]

PUBLIC_ROUTERS = [registration.router for registration in ROUTER_REGISTRATIONS if registration.audience == "public"]
TRUST_ROUTERS = [registration.router for registration in ROUTER_REGISTRATIONS if registration.audience == "trust"]


DEV_ENV_VALUES = {"dev", "development", "local", "test"}


def _is_dev_environment(environment: str) -> bool:
    return environment.strip().lower() in DEV_ENV_VALUES


def iter_route_policy_specs() -> list[dict[str, str]]:
    specs: list[dict[str, str]] = []
    for registration in ROUTER_REGISTRATIONS:
        prefix = registration.policy_path or registration.router.prefix
        if not prefix:
            continue
        specs.append(
            {
                "path": prefix,
                "policy_name": registration.access_policy,
                "registration_name": registration.policy_name,
            }
        )
        specs.append(
            {
                "path": f"/v3{prefix}",
                "policy_name": registration.access_policy,
                "registration_name": f"{registration.policy_name}_v3",
            }
        )
    return specs


def register_routers(
    app: FastAPI,
    *,
    enable_experimental_api: bool,
    environment: str = "development",
) -> None:
    """Register /api + /v3 routers, with optional experimental version tracks."""
    include_trust = True
    registrations = [
        registration
        for registration in ROUTER_REGISTRATIONS
        if registration.audience == "public" or include_trust
    ]
    routers = [registration.router for registration in registrations]

    for router in routers:
        app.include_router(router)

    for router in routers:
        app.include_router(router, prefix="/v3")

    if enable_experimental_api:
        for prefix in ("/v2", "/v4", "/v5"):
            for router in routers:
                app.include_router(router, prefix=prefix)
