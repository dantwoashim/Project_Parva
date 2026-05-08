"""Effective cutoff diagnostics for reconstructed month starts."""

from __future__ import annotations

from typing import Any

PUBLICATION_STATUS = "computed_prediction_not_official"


def estimate_effective_cutoffs(features: list[dict[str, Any]]) -> dict[str, Any]:
    buckets: dict[str, list[int]] = {}
    for row in features:
        month = int(row["bs_month"])
        buckets.setdefault(str(month), []).append(int(row["month_length"]))
    surfaces = {
        month: {
            "median_observed_month_length": sorted(values)[len(values) // 2],
            "case_count": len(values),
            "cutoff_status": "requires_solar_ingress_cache_for_minute_level_cutoff",
        }
        for month, values in buckets.items()
    }
    return {
        "publication_status": PUBLICATION_STATUS,
        "surfaces": surfaces,
        "limitation": "The current public witness corpus reconstructs starts; exact solar-ingress minute offsets require trusted ephemeris cache.",
    }
