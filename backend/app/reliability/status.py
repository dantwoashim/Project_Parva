"""Runtime reliability status helpers."""

from __future__ import annotations

import logging
from typing import Any

from app.bootstrap.settings import load_settings
from app.cache import get_cache_stats, measure_hotset_latency
from app.calendar.ephemeris.swiss_eph import get_ephemeris_info
from app.reliability.metrics import get_metrics_registry
from app.services.runtime_cache import stats as runtime_cache_stats

logger = logging.getLogger(__name__)


def get_runtime_status() -> dict[str, Any]:
    settings = load_settings()
    ephemeris = get_ephemeris_info()
    cache = get_cache_stats()
    hotset_latency = measure_hotset_latency()
    runtime_cache = runtime_cache_stats()
    cache_ready = cache.get("file_count", 0) > 0
    freshness = cache.get("freshness", {})
    newest_age_seconds = freshness.get("newest_age_seconds")
    stale_threshold_seconds = settings.precomputed_stale_hours * 3600
    cache_stale = bool(
        cache_ready
        and newest_age_seconds is not None
        and newest_age_seconds > stale_threshold_seconds
    )

    status = "healthy"
    warnings = []
    if ephemeris.get("mode") == "fallback":
        status = "degraded"
        warnings.append("ephemeris_fallback_mode")
    if not cache_ready:
        warnings.append("no_precomputed_artifacts")
        if settings.require_precomputed:
            status = "degraded"
            warnings.append("precomputed_required_but_missing")
    if cache_stale:
        status = "degraded"
        warnings.append("precomputed_artifacts_stale")

    metrics = get_metrics_registry()
    for warning in warnings:
        metrics.record_degraded_state(warning)
    if warnings:
        logger.warning("Runtime degraded signals: %s", ",".join(warnings))

    return {
        "status": status,
        "warnings": warnings,
        "product_signals": {
            "surface_visible": [
                "status",
                "warnings",
                "ephemeris.mode",
                "cache.required",
                "cache.freshness",
                "cache.hotset_latency",
            ],
            "telemetry_only": [
                "endpoint_request_counts",
                "latency_p95_ms",
                "cache_hit_ratios",
                "degraded_state_counters",
                "runtime_cache",
                "runtime_cache_evictions",
            ],
        },
        "ephemeris": ephemeris,
        "cache": {
            "file_count": cache.get("file_count", 0),
            "total_bytes": cache.get("total_bytes", 0),
            "required": settings.require_precomputed,
            "stale_threshold_hours": settings.precomputed_stale_hours,
            "freshness": freshness,
            "artifact_classes": cache.get("artifact_classes", {}),
            "hotset_latency": hotset_latency,
        },
        "runtime_cache": runtime_cache,
        "metrics": metrics.snapshot(),
    }
