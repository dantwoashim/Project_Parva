"""Search explainable rule programs over reconstructed month-start features."""

from __future__ import annotations

from typing import Any

from app.future_bs.month_start.month_start_features import build_month_start_features

from .program_score import score_program
from .rule_dsl import CANDIDATE_PROGRAMS

PUBLICATION_STATUS = "computed_prediction_not_official"


def run_program_synthesis(features_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    features_payload = features_payload or build_month_start_features()
    features = features_payload.get("features", [])
    scored = [score_program(program, features) for program in CANDIDATE_PROGRAMS]
    scored.sort(key=lambda row: (row["score"], -row["complexity"]), reverse=True)
    return {
        "publication_status": PUBLICATION_STATUS,
        "synthesis_mode": "minimal_viable_rule_dsl_grid",
        "case_count": len(features),
        "selected_program": scored[0] if scored else None,
        "programs": scored,
        "limitation": "This is an explainable bounded DSL search; exact solar cutoff synthesis remains gated by trusted ingress features.",
    }
