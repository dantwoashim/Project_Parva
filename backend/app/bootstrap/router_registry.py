"""Router registration for public and experimental API profiles."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import APIRouter, FastAPI

from app.api import (
    agent_router,
    billing_router,
    cache_router,
    calendar_model_risk_private_router,
    calendar_model_risk_router,
    calendar_router,
    compliance_router,
    engine_router,
    enterprise_router,
    explain_router,
    feed_router,
    festival_router,
    festival_timeline_router,
    forecast_router,
    future_bs_private_router,
    future_bs_router,
    glossary_router,
    impact_router,
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
    protocol_router,
    provenance_router,
    public_artifacts_router,
    public_demo_calendar_router,
    reliability_router,
    resolve_router,
    rules_router,
    spec_router,
    temporal_compass_router,
    timegraph_router,
    trust_router,
)


@dataclass(frozen=True)
class RouterRegistration:
    router: APIRouter
    audience: str
    access_policy: str
    policy_name: str
    policy_path: str | None = None
    include_v3: bool = True
    include_base: bool = True
    include_experimental_versions: bool = True
    register_when_experimental_enabled: bool = False
    include_in_policy_specs: bool = True


ROUTER_REGISTRATIONS = [
    # Keep timeline router before dynamic /festivals/{festival_id} routes.
    RouterRegistration(festival_timeline_router, "public", "public", "festivals_timeline"),
    RouterRegistration(festival_router, "public", "public", "festivals"),
    RouterRegistration(calendar_router, "public", "public", "calendar"),
    RouterRegistration(enterprise_router, "public", "public", "enterprise"),
    RouterRegistration(compliance_router, "public", "public", "compliance"),
    RouterRegistration(
        future_bs_router,
        "public",
        "public",
        "future_bs",
        policy_path="/v4/api/future-bs/capabilities",
        include_v3=False,
        include_experimental_versions=False,
    ),
    RouterRegistration(
        future_bs_private_router,
        "private",
        "experimental_read",
        "future_bs_private",
        include_v3=False,
        include_experimental_versions=False,
        register_when_experimental_enabled=True,
        include_in_policy_specs=False,
    ),
    RouterRegistration(
        calendar_model_risk_router,
        "public",
        "public",
        "calendar_model_risk",
        policy_path="/v5/api/calendar-model-risk/capabilities",
        include_v3=False,
        include_experimental_versions=False,
    ),
    RouterRegistration(
        calendar_model_risk_private_router,
        "private",
        "experimental_read",
        "calendar_model_risk_private",
        include_v3=False,
        include_experimental_versions=False,
        register_when_experimental_enabled=True,
        include_in_policy_specs=False,
    ),
    RouterRegistration(billing_router, "public", "public", "billing", policy_path="/api/billing"),
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
    RouterRegistration(timegraph_router, "trust", "timegraph_read", "timegraph"),
    RouterRegistration(trust_router, "trust", "trust_read", "trust"),
    RouterRegistration(rules_router, "trust", "rules_read", "rules"),
    RouterRegistration(impact_router, "trust", "impact_read", "impact"),
    RouterRegistration(agent_router, "trust", "agent_read", "agent"),
    RouterRegistration(protocol_router, "trust", "protocol_read", "protocol"),
]

PUBLIC_ROUTERS = [registration.router for registration in ROUTER_REGISTRATIONS if registration.audience == "public"]
TRUST_ROUTERS = [registration.router for registration in ROUTER_REGISTRATIONS if registration.audience == "trust"]

PUBLIC_DEMO_ROUTE_REGISTRATIONS = [
    RouterRegistration(
        public_demo_calendar_router,
        "public",
        "public",
        "calendar_public_demo",
        policy_path="/v3/api/calendar",
        include_v3=True,
        include_base=False,
        include_experimental_versions=False,
    ),
    RouterRegistration(
        future_bs_router,
        "public",
        "public",
        "future_bs_public_demo",
        policy_path="/v4/api/future-bs/capabilities",
        include_v3=False,
        include_experimental_versions=False,
    ),
    RouterRegistration(trust_router, "trust", "trust_read", "trust"),
    RouterRegistration(timegraph_router, "trust", "timegraph_read", "timegraph"),
    RouterRegistration(rules_router, "trust", "rules_read", "rules"),
]


DEV_ENV_VALUES = {"dev", "development", "local", "test"}


def _is_dev_environment(environment: str) -> bool:
    return environment.strip().lower() in DEV_ENV_VALUES


def iter_route_policy_specs() -> list[dict[str, str]]:
    specs: list[dict[str, str]] = []
    for registration in ROUTER_REGISTRATIONS:
        if not registration.include_in_policy_specs:
            continue
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
        if registration.include_v3:
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
    show_private_schema: bool = False,
    environment: str = "development",
    route_profile: str = "full",
) -> None:
    """Register /api + /v3 routers, with optional experimental version tracks."""
    include_trust = True
    if route_profile == "public_demo":
        registrations = PUBLIC_DEMO_ROUTE_REGISTRATIONS
    else:
        registrations = [
            registration
            for registration in ROUTER_REGISTRATIONS
            if registration.audience == "public"
            or (include_trust and registration.audience == "trust")
            or (enable_experimental_api and registration.register_when_experimental_enabled)
        ]
    for registration in registrations:
        if registration.include_base:
            app.include_router(
                registration.router,
                include_in_schema=(
                    show_private_schema if registration.register_when_experimental_enabled else True
                ),
            )

    for registration in registrations:
        if registration.include_v3:
            app.include_router(
                registration.router,
                prefix="/v3",
                include_in_schema=(
                    show_private_schema if registration.register_when_experimental_enabled else True
                ),
            )

    if enable_experimental_api:
        for prefix in ("/v2", "/v4", "/v5"):
            for registration in registrations:
                if registration.include_experimental_versions:
                    app.include_router(
                        registration.router,
                        prefix=prefix,
                        include_in_schema=(
                            show_private_schema
                            if registration.register_when_experimental_enabled
                            else True
                        ),
                    )
