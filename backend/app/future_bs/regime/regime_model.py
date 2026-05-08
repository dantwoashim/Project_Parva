"""Regime labels for reconstructed BS month-start rows."""

from __future__ import annotations

from typing import Any

from app.future_bs.month_start.month_start_features import build_month_start_features

from .change_point_detection import detect_change_points

PUBLICATION_STATUS = "computed_prediction_not_official"


def _regime_for(row: dict[str, Any]) -> str:
    year = int(row["bs_year"])
    tier = int(row["best_source_tier"])
    if tier == 1 and year >= 2078:
        return "recent_official"
    if tier <= 4 and year >= 2071:
        return "publisher_consensus"
    if tier <= 2:
        return "modern_official"
    if year < 2050:
        return "older_traditional"
    return "unknown_or_mixed"


def assign_regimes(features_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    features_payload = features_payload or build_month_start_features()
    assignments = [
        {
            "bs_year": row["bs_year"],
            "bs_month": row["bs_month"],
            "regime": _regime_for(row),
            "best_source_tier": row["best_source_tier"],
            "agreement_score": row["agreement_score"],
        }
        for row in features_payload.get("features", [])
    ]
    return {
        "publication_status": PUBLICATION_STATUS,
        "assignments": assignments,
    }


def detect_regime_changes(features_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    features_payload = features_payload or build_month_start_features()
    assignments = assign_regimes(features_payload)
    changes = detect_change_points(features_payload.get("features", []))
    counts: dict[str, int] = {}
    for row in assignments["assignments"]:
        counts[row["regime"]] = counts.get(row["regime"], 0) + 1
    return {
        "publication_status": PUBLICATION_STATUS,
        "regime_counts": counts,
        "change_points": changes["change_points"],
        "assignments": assignments["assignments"],
    }
