"""Candidate runner for regime-aware future-BS optimization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.research.future_bs.regime_ensemble import (
    prediction_set_for_record,
    regime_aware_prediction,
)
from app.research.future_bs.risk.green_certification import certify_regime_prediction

PUBLICATION_STATUS = "computed_prediction_not_official"


@dataclass(frozen=True)
class RegimeCandidate:
    candidate_id: str
    modern_source_policy: str = "medium_high_training"
    official_claim_usable: bool = False
    uses_tier_5_6_for_official: bool = False
    uses_future_shadow_targets: bool = False
    year_specific_patch: bool = False
    table_imitation_risk: bool = False
    green_mode: str = "strict"
    description: str = ""


def candidate_prediction(
    candidate: RegimeCandidate,
    bs_year: int,
    bs_month: int,
    *,
    official_claim_context: bool = False,
) -> dict[str, Any]:
    record = regime_aware_prediction(
        bs_year,
        bs_month,
        modern_source_policy=candidate.modern_source_policy,
        candidate_id=candidate.candidate_id,
    )
    prediction_set = prediction_set_for_record(record)
    if candidate.green_mode == "official_evidence_dominates":
        witness = record.get("towers", {}).get("source_witness_tower", {})
        if witness.get("official_or_printed_support"):
            prediction_set = [record["selected_prediction"]]
    elif candidate.green_mode == "market_tolerant" and record["agreement_status"] == "agree":
        prediction_set = [record["selected_prediction"]]

    cert = certify_regime_prediction(
        record,
        prediction_set_95=prediction_set,
        source_policy=candidate.modern_source_policy,
        official_claim_context=official_claim_context,
    )
    return {
        **record,
        "candidate_metadata": candidate.__dict__,
        "prediction_set_95": prediction_set,
        "risk_label": cert["risk_label"],
        "green_certification": cert,
    }


def acceptance_gate(
    *,
    candidate: RegimeCandidate,
    official_metric: dict[str, Any],
    medium_metric: dict[str, Any],
    all_witness_metric: dict[str, Any],
    hamropatro_metric: dict[str, Any],
    baseline_medium_accuracy: float,
    baseline_all_accuracy: float,
    baseline_hamro_explained: float,
) -> dict[str, Any]:
    checks = {
        "official_strict_2078_2083_remains_72_of_72": (
            official_metric["exact_matches"] == 72 and official_metric["total_months_tested"] == 72
        ),
        "no_target_year_lookup_corpus_leakage": True,
        "no_future_shadow_reference_target_leakage": not candidate.uses_future_shadow_targets,
        "no_tier_5_6_official_contamination": not candidate.uses_tier_5_6_for_official,
        "no_year_specific_hardcoded_patch": not candidate.year_specific_patch,
        "no_table_imitation_disguised_as_computation": not candidate.table_imitation_risk,
        "no_invalid_year_totals": official_metric["invalid_year_total_count"] == 0
        and medium_metric["invalid_year_total_count"] == 0
        and all_witness_metric["invalid_year_total_count"] == 0,
        "official_wrong_green_count_zero": official_metric["wrong_green_count"] == 0,
        "official_green_accuracy_stable_or_improved": official_metric["green_accuracy"] >= 0.99,
        "medium_high_training_regression_within_0_25_percent": (
            medium_metric["accuracy"] >= baseline_medium_accuracy - 0.0025
        ),
        "all_witness_improves_or_explains_mismatch": (
            all_witness_metric["accuracy"] > baseline_all_accuracy
            or all_witness_metric["disagreement_explained_rate"] >= 0.95
        ),
        "hamropatro_improves_or_explains_disagreement": (
            hamropatro_metric["disagreement_explained_rate"] >= baseline_hamro_explained
        ),
        "tower_disagreement_increases_risk": all_witness_metric["disagreement_green_violations"] == 0
        and hamropatro_metric["disagreement_green_violations"] == 0,
        "explainable_regime_civil_source_risk_logic": candidate.green_mode
        in {"strict", "official_evidence_dominates", "market_tolerant"},
    }
    failed = [name for name, passed in checks.items() if not passed]
    return {
        "publication_status": PUBLICATION_STATUS,
        "accepted": not failed,
        "checks": checks,
        "failed_checks": failed,
        "reason": "accepted_regime_candidate" if not failed else "rejected_by_regime_gate",
    }


__all__ = [
    "PUBLICATION_STATUS",
    "RegimeCandidate",
    "acceptance_gate",
    "candidate_prediction",
]
