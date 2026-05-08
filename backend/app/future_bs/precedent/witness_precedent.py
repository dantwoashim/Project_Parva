"""Witness-aware precedent case extraction."""

from __future__ import annotations

from typing import Any

from app.future_bs.month_start.month_start_features import build_month_start_features

PUBLICATION_STATUS = "computed_prediction_not_official"


def build_witness_precedent_cases(features_payload: dict[str, Any] | None = None, limit: int = 100) -> dict[str, Any]:
    features_payload = features_payload or build_month_start_features()
    features = sorted(
        features_payload.get("features", []),
        key=lambda row: (
            int(row.get("boundary_sensitive_month") is True),
            float(row.get("agreement_score") or 0),
            -int(row.get("best_source_tier") or 9),
        ),
        reverse=True,
    )
    cases = []
    for row in features[:limit]:
        cases.append(
            {
                "bs_year": row["bs_year"],
                "bs_month": row["bs_month"],
                "month_length": row["month_length"],
                "previous_month_length": row["previous_month_length"],
                "year_mod_19": row["year_mod_19"],
                "year_mod_28": row["year_mod_28"],
                "year_mod_57": row["year_mod_57"],
                "agreement_score": row["agreement_score"],
                "best_source_tier": row["best_source_tier"],
                "boundary_sensitive_month": row["boundary_sensitive_month"],
            }
        )
    return {
        "publication_status": PUBLICATION_STATUS,
        "case_count": len(cases),
        "cases": cases,
    }
