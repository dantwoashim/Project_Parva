"""Runtime reliability status helpers."""

from __future__ import annotations

from typing import Any

from app.cache import get_cache_stats
from app.calendar.ephemeris.swiss_eph import get_ephemeris_info


def get_runtime_status() -> dict[str, Any]:
    ephemeris = get_ephemeris_info()
    cache = get_cache_stats()
    cache_ready = cache.get("file_count", 0) > 0

    status = "healthy"
    warnings = []
    if ephemeris.get("mode") == "fallback":
        status = "degraded"
        warnings.append("ephemeris_fallback_mode")
    if not cache_ready:
        warnings.append("no_precomputed_artifacts")

    return {
        "status": status,
        "warnings": warnings,
        "ephemeris": ephemeris,
        "cache": {
            "file_count": cache.get("file_count", 0),
            "total_bytes": cache.get("total_bytes", 0),
        },
    }
