"""Canonical runtime engine manifest for public Parva routes."""

from __future__ import annotations

from typing import Any

from .ephemeris_config import get_ephemeris_config

CANONICAL_ENGINE_ID = "parva-v3-canonical"
CANONICAL_MANIFEST_VERSION = "2026-03-20"


PUBLIC_ROUTE_FAMILIES: tuple[dict[str, Any], ...] = (
    {
        "family": "calendar_core",
        "paths": [
            "/api/calendar/convert",
            "/api/calendar/today",
            "/api/calendar/panchanga",
            "/api/calendar/tithi",
        ],
        "canonical_runtime": [
            "app.calendar.routes",
            "app.calendar.bikram_sambat",
            "app.calendar.panchanga",
            "app.calendar.tithi",
        ],
        "compatibility_components": [],
    },
    {
        "family": "festival_rules",
        "paths": [
            "/api/festivals/*",
            "/api/calendar/festivals/calculate/{festival_id}",
            "/api/calendar/festivals/upcoming",
        ],
        "canonical_runtime": [
            "app.rules.service.FestivalRuleService",
            "app.calendar.calculator_v2",
            "app.rules.catalog_v4",
        ],
        "compatibility_components": [
            "app.calendar.calculator",
            "app.calendar.festival_rules.json",
        ],
    },
    {
        "family": "personal_stack",
        "paths": [
            "/api/personal/*",
            "/api/muhurta/*",
            "/api/kundali/*",
            "/api/temporal/*",
        ],
        "canonical_runtime": [
            "app.api.personal_routes",
            "app.api.muhurta_routes",
            "app.api.kundali_routes",
            "app.api.temporal_compass_routes",
            "app.calendar.panchanga",
            "app.calendar.muhurta",
            "app.calendar.kundali",
        ],
        "compatibility_components": [],
    },
)


def build_engine_manifest() -> dict[str, Any]:
    cfg = get_ephemeris_config()
    return {
        "manifest_version": CANONICAL_MANIFEST_VERSION,
        "canonical_engine_id": CANONICAL_ENGINE_ID,
        "engine_version": "v3",
        "ephemeris": {
            "mode": cfg.ephemeris_mode,
            "ayanamsa": cfg.ayanamsa,
            "coordinate_system": cfg.coordinate_system,
            "header": cfg.header_value,
        },
        "festival_runtime": {
            "service": "app.rules.service.FestivalRuleService",
            "calculator": "app.calendar.calculator_v2",
            "catalog": "app.rules.catalog_v4",
            "legacy_compatibility": [
                "app.calendar.calculator",
                "app.calendar.festival_rules.json",
            ],
        },
        "public_route_families": list(PUBLIC_ROUTE_FAMILIES),
    }
