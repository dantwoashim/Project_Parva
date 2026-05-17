"""Public non-official commitment log entries."""

from __future__ import annotations


def forecast_commitment(claim: dict) -> dict:
    return {
        "kind": "forecast_commitment",
        "claim": claim,
        "publication_status": "computed_prediction_not_official",
        "review_required": True,
        "claim_boundary": "research_forecast_not_official",
    }
