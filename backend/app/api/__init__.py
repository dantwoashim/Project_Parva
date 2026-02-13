"""API package exports."""

from .calendar_routes import router as calendar_router
from .cache_routes import router as cache_router
from .explain_routes import router as explain_router
from .feed_routes import router as feed_router
from .festival_routes import router as festival_router
from .forecast_routes import router as forecast_router
from .location_routes import router as locations_router
from .observance_routes import router as observance_router
from .policy_routes import router as policy_router
from .provenance_routes import router as provenance_router
from .reliability_routes import router as reliability_router
from .webhook_routes import router as webhook_router
from .engine_routes import router as engine_router
from .resolve_routes import router as resolve_router
from .spec_routes import router as spec_router
from .integration_feed_routes import router as integration_feed_router
from .public_artifacts_routes import router as public_artifacts_router

__all__ = [
    "calendar_router",
    "cache_router",
    "explain_router",
    "feed_router",
    "festival_router",
    "forecast_router",
    "locations_router",
    "observance_router",
    "policy_router",
    "provenance_router",
    "reliability_router",
    "webhook_router",
    "engine_router",
    "resolve_router",
    "spec_router",
    "integration_feed_router",
    "public_artifacts_router",
]
