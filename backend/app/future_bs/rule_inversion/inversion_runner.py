"""Run hidden-rule inversion against reconstructed month-start features."""

from __future__ import annotations

from typing import Any

from app.future_bs.month_start.month_start_features import build_month_start_features

from .decision_surface import score_decision_surfaces
from .effective_cutoff import estimate_effective_cutoffs

PUBLICATION_STATUS = "computed_prediction_not_official"


def run_hidden_rule_inversion(features_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    features_payload = features_payload or build_month_start_features()
    features = features_payload.get("features", [])
    surfaces = estimate_effective_cutoffs(features)
    programs = score_decision_surfaces(features)
    return {
        "publication_status": PUBLICATION_STATUS,
        "case_count": len(features),
        "selected_rule_family": "source_weighted_month_start_consensus",
        "candidate_surfaces": programs,
        "effective_cutoff_surfaces": surfaces,
        "no_leakage_note": "This inversion uses reconstructed historical rows only; future rows remain computed_prediction_not_official.",
    }
