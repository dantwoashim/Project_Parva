"""Simple change-point diagnostics over source tiers and conflict rates."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

PUBLICATION_STATUS = "computed_prediction_not_official"


def detect_change_points(features: list[dict[str, Any]]) -> dict[str, Any]:
    by_decade: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in features:
        by_decade[(int(row["bs_year"]) // 10) * 10].append(row)
    change_points = []
    previous_tier = None
    for decade in sorted(by_decade):
        rows = by_decade[decade]
        avg_tier = sum(int(row["best_source_tier"]) for row in rows) / len(rows)
        if previous_tier is not None and abs(avg_tier - previous_tier) >= 1.5:
            change_points.append({"bs_year": decade, "reason": "source_tier_regime_shift", "avg_tier": round(avg_tier, 3)})
        previous_tier = avg_tier
    return {"publication_status": PUBLICATION_STATUS, "change_points": change_points}
