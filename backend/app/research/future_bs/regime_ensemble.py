"""Regime-aware future-BS ensemble with source-policy separation."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from app.calendar.constants import BS_MONTH_NAMES

from .market_shadow import hamropatro_shadow_month, legacy_static_month
from .regime.regime_detector import detect_regime
from .solar_ingress_predictor import predict_solar_ingress_year
from .source_policy import policy_rows
from .unified_predictor import UNIFIED_MODEL_ID, predict_unified_future_bs_year

PUBLICATION_STATUS = "computed_prediction_not_official"
DEFAULT_TRAIN_START = 2000
PUBLIC_TRAIN_END = 2083
DEFAULT_MODERN_SOURCE_POLICY = "medium_high_training"


@lru_cache(maxsize=2048)
def _solar_year(
    bs_year: int,
    train_start: int = DEFAULT_TRAIN_START,
    source_policy: str = DEFAULT_MODERN_SOURCE_POLICY,
) -> tuple[int, ...]:
    train_end = min(int(bs_year) - 1, PUBLIC_TRAIN_END)
    if train_end >= train_start:
        payload = predict_unified_future_bs_year(
            int(bs_year),
            train_start=train_start,
            train_end=train_end,
        )
    else:
        # BS 2000 has no earlier row in this research corpus. It remains a
        # non-causal bootstrap diagnostic and is excluded by the leakage audit.
        payload = predict_solar_ingress_year(
            int(bs_year),
            train_start=train_start,
            train_end=train_start,
            source_policy="all_reference",
        )
    return tuple(int(value) for value in payload["months"])


@lru_cache(maxsize=1)
def _witness_index() -> dict[tuple[int, int], dict[str, Any]]:
    index: dict[tuple[int, int], dict[str, Any]] = {}
    for policy in ("official_strict", "medium_high_training", "all_witness_experimental"):
        for row in policy_rows(policy):
            key = (int(row["bs_year"]), int(row["bs_month"]))
            current = index.get(key)
            tier = int(row.get("best_source_tier") or 99)
            if current is None or tier < int(current.get("best_source_tier") or 99):
                index[key] = {
                    "best_source_tier": tier,
                    "verification_status": row.get("verification_status", ""),
                    "agreement_score": float(row.get("agreement_score") or 0.0),
                    "manual_review_required": str(row.get("manual_review_required", "")).lower() == "true",
                    "usable_for_official_claim": row.get("usable_for_official_claim") == "true",
                    "usable_for_training": row.get("usable_for_training") == "true",
                    "source_policy": policy,
                }
    return index


def source_witness_tower(bs_year: int, bs_month: int) -> dict[str, Any]:
    witness = _witness_index().get((int(bs_year), int(bs_month)))
    if not witness:
        return {
            "best_source_tier": None,
            "witness_strength": "none",
            "source_conflict": False,
            "official_or_printed_support": False,
            "source_policy_contamination": False,
        }
    tier = int(witness["best_source_tier"])
    return {
        **witness,
        "witness_strength": "high" if tier <= 2 else "medium" if tier <= 4 else "weak",
        "source_conflict": bool(witness.get("manual_review_required")),
        "official_or_printed_support": tier <= 2,
        "source_policy_contamination": tier >= 5 and bool(witness.get("usable_for_official_claim")),
    }


def regime_aware_prediction(
    bs_year: int,
    bs_month: int,
    *,
    train_start: int = DEFAULT_TRAIN_START,
    modern_source_policy: str = DEFAULT_MODERN_SOURCE_POLICY,
    candidate_id: str = "baseline_regime_aware_solar_civil",
) -> dict[str, Any]:
    bs_year = int(bs_year)
    bs_month = int(bs_month)
    solar_months = list(_solar_year(bs_year, train_start, modern_source_policy))
    solar_days = solar_months[bs_month - 1]
    chronological_train_end = min(bs_year - 1, PUBLIC_TRAIN_END)
    past_only = chronological_train_end >= train_start
    effective_train_end = chronological_train_end if past_only else train_start
    legacy_days = legacy_static_month(bs_year, bs_month)
    hamro_days = hamropatro_shadow_month(bs_year, bs_month)
    witness = source_witness_tower(bs_year, bs_month)
    boundary_sensitive = abs(solar_days - legacy_days) >= 1 and bs_month in {6, 7, 8, 9, 10, 11, 12}
    regime = detect_regime(
        bs_year=bs_year,
        bs_month=bs_month,
        solar_civil_prediction=solar_days,
        legacy_static_prediction=legacy_days,
        hamropatro_shadow_prediction=hamro_days,
        best_source_tier=witness.get("best_source_tier"),
        source_conflict=bool(witness.get("source_conflict")),
        boundary_sensitive=boundary_sensitive,
    )

    market_values = {legacy_days}
    if hamro_days is not None:
        market_values.add(hamro_days)
    towers = {
        "modern_official_solar_civil_tower": {
            "prediction": solar_days,
            "source_policy": "source_stratified",
            "requested_diagnostic_source_policy": modern_source_policy,
            "model_id": UNIFIED_MODEL_ID,
            "official_claim_usable": False,
        },
        "legacy_market_continuity_tower": {
            "prediction": legacy_days,
            "hamropatro_shadow_prediction": hamro_days,
            "official_claim_usable": False,
        },
        "source_witness_tower": witness,
        "regime_detector": regime,
    }
    disagreement_type = "all_towers_agree" if len({solar_days, *market_values}) == 1 else "solar_market_disagreement"
    year_total = sum(solar_months)
    return {
        "publication_status": PUBLICATION_STATUS,
        "candidate_id": candidate_id,
        "bs_year": bs_year,
        "bs_month": bs_month,
        "month_name": BS_MONTH_NAMES[bs_month - 1],
        "selected_prediction": solar_days,
        "solar_civil_prediction": solar_days,
        "legacy_static_prediction": legacy_days,
        "hamropatro_shadow_prediction": hamro_days,
        "selected_tower": "modern_official_solar_civil_tower",
        "prediction_training_end_bs_year": effective_train_end,
        "selected_prediction_past_only": past_only,
        "source_policy": "source_stratified",
        "requested_diagnostic_source_policy": modern_source_policy,
        "model_id": UNIFIED_MODEL_ID,
        "regime_assignment": regime["regime_assignment"],
        "agreement_status": "agree" if disagreement_type == "all_towers_agree" else "disagree",
        "disagreement_type": disagreement_type,
        "boundary_sensitive": boundary_sensitive,
        "year_total": year_total,
        "year_total_valid": year_total in {365, 366},
        "source_conflict_risk": bool(witness.get("source_conflict")),
        "source_policy_contamination": bool(witness.get("source_policy_contamination")),
        "towers": towers,
    }


def prediction_set_for_record(record: dict[str, Any]) -> list[int]:
    values = {int(record["solar_civil_prediction"]), int(record["legacy_static_prediction"])}
    if record.get("hamropatro_shadow_prediction") is not None:
        values.add(int(record["hamropatro_shadow_prediction"]))
    return sorted(values)


__all__ = [
    "DEFAULT_MODERN_SOURCE_POLICY",
    "PUBLICATION_STATUS",
    "prediction_set_for_record",
    "regime_aware_prediction",
    "source_witness_tower",
]
