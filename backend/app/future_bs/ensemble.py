"""Solar-ingress plus legacy-cycle future BS prediction ensemble."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.calendar.constants import BS_MAX_YEAR, BS_MIN_YEAR, BS_MONTH_NAMES
from app.calendar.provenance import get_bs_year_provenance

from .confidence import confidence_label as _confidence_label
from .confidence import horizon_factor as _horizon_factor
from .corpus import (
    corpus_range_label,
    get_corpus_row,
    is_known_year,
    known_months,
    source_label_for_year,
)
from .legacy_cycle_predictor import predict_from_training
from .models import CALIBRATION_VERSION, METHOD_VERSION, MONTH_DAY_VALUES, PREDICTION_MAX_YEAR
from .precomputed_store import get_precomputed_year, live_compute_enabled
from .run_registry import DEFAULT_RUN_ID
from .solar_ingress_engine import active_ephemeris_label
from .solar_ingress_predictor import DEFAULT_REFERENCE_TRAIN_END
from .statistical_pattern_predictor import predict_stacked_year
from .year_total_gate import apply_year_total_gate


def _validate_year(bs_year: int) -> None:
    if bs_year < BS_MIN_YEAR or bs_year > PREDICTION_MAX_YEAR:
        raise ValueError(
            f"BS year {bs_year} is outside the future-BS engine range "
            f"({BS_MIN_YEAR}-{PREDICTION_MAX_YEAR})."
        )


def _constraint_checks(months: list[int]) -> dict[str, Any]:
    total_days = sum(months)
    return {
        "valid_month_lengths": all(days in MONTH_DAY_VALUES for days in months),
        "year_total_days": total_days,
        "plausible_year_total": 354 <= total_days <= 368,
        "allowed_month_lengths": list(MONTH_DAY_VALUES),
    }


def _ephemeris_status() -> str:
    return (
        "jpl_de440_lahiri_sidereal"
        if active_ephemeris_label() == "jpl_de440"
        else "swiss_moshier_lahiri_sidereal"
    )


def _source_payload(bs_year: int) -> dict[str, Any]:
    provenance = get_bs_year_provenance(bs_year)
    corpus_row = get_corpus_row(bs_year) if is_known_year(bs_year) else None
    return {
        "type": source_label_for_year(bs_year) if is_known_year(bs_year) else "computed_prediction",
        "status": provenance.source_status,
        "source_status": corpus_row.verification_status if corpus_row else "computed_prediction",
        "source_reference": corpus_row.source_reference if corpus_row else "computational_solar_ingress",
        "source_quality": corpus_row.source_quality if corpus_row else 0.0,
        "structured_official_range": provenance.official_structured_range,
        "static_lookup_range": provenance.static_lookup_range,
        "note": provenance.note,
    }


def _computed_source_payload(bs_year: int) -> dict[str, Any]:
    supporting = _source_payload(bs_year)
    return {
        "type": "computed_prediction",
        "status": "computed_solar_ingress",
        "source_status": "computed_prediction",
        "source_reference": "computational_solar_ingress",
        "source_quality": 0.0,
        "supporting_corpus_source": supporting if is_known_year(bs_year) else None,
        "structured_official_range": supporting["structured_official_range"],
        "static_lookup_range": supporting["static_lookup_range"],
        "note": (
            "Future-BS output is computed and is not an official publication. "
            "Any supporting static corpus row is treated as review evidence, not final authority."
        ),
    }


def _known_year_payload(bs_year: int) -> dict[str, Any]:
    months = known_months(bs_year)
    provenance = get_bs_year_provenance(bs_year)
    known_official = provenance.confidence == "official"
    confidence_score = 1.0 if known_official else 0.92
    details = []
    for index, days in enumerate(months, start=1):
        details.append(
            {
                "month": index,
                "month_name": BS_MONTH_NAMES[index - 1],
                "final_days": days,
                "probability": {f"{value}_days": 1.0 if value == days else 0.0 for value in MONTH_DAY_VALUES},
                "confidence_score": confidence_score,
                "confidence_label": _confidence_label(confidence_score, known_official=known_official),
                "model_agreement": "corpus",
                "risk_flags": [],
            }
        )
    return {
        "bs_year": bs_year,
        "months": months,
        "month_details": details,
        "year_total": sum(months),
        "confidence_score": confidence_score,
        "confidence": _confidence_label(confidence_score, known_official=known_official),
        "risk_flags": [],
        "constraints": _constraint_checks(months),
        "method_version": METHOD_VERSION,
        "calibration_version": CALIBRATION_VERSION,
        "run_id": DEFAULT_RUN_ID,
        "model_family": "known_corpus",
        "source": _source_payload(bs_year),
        "computational_model_outputs": [],
        "legacy_model_output": None,
        "model_agreement": "corpus",
        "engine_components": [
            "verified_month_length_corpus",
            "solar_ingress_computational_model",
            "legacy_cycle_fallback_model",
            "probabilistic_confidence_scoring",
            "loan_contract_risk_adapter",
        ],
        "limits": {
            "known_static_lookup": corpus_range_label(),
            "prediction_range": f"{BS_MIN_YEAR}-{PREDICTION_MAX_YEAR} BS",
            "ephemeris_status": _ephemeris_status(),
            "publication_status": "computed_prediction_not_official",
        },
        "source_status": _source_payload(bs_year)["source_status"],
        "publication_status": "computed_prediction_not_official",
        "legacy_publication_status": "not_official_publication",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _future_year_payload(bs_year: int) -> dict[str, Any]:
    stacked = predict_stacked_year(bs_year)
    solar = stacked["solar"]
    baseline_months, baseline_models = predict_from_training(
        bs_year,
        BS_MIN_YEAR,
        DEFAULT_REFERENCE_TRAIN_END,
    )
    statistical = stacked.get("statistical")
    statistical_months = statistical["months"] if statistical else baseline_months
    horizon = _horizon_factor(bs_year, BS_MAX_YEAR)
    details = []
    final_months: list[int] = []
    all_risk_flags = set([*solar["risk_flags"], *stacked.get("risk_flags", [])])
    all_risk_flags.add("outside_static_lookup")
    if bs_year > BS_MAX_YEAR + 50:
        all_risk_flags.add("long_horizon")

    for index in range(12):
        solar_days = solar["months"][index]
        baseline_days = baseline_months[index]
        stacked_detail = stacked["month_details"][index]
        statistical_days = statistical_months[index]
        final_days = stacked_detail["final_days"]
        probability = stacked_detail["probability"]
        confidence_score = round(float(stacked_detail["confidence_score"]) * horizon, 4)
        risk_flags = list(stacked_detail.get("risk_flags", []))
        if bs_year > BS_MAX_YEAR:
            risk_flags.append("outside_static_lookup")
        if bs_year > BS_MAX_YEAR + 50:
            risk_flags.append("long_horizon")
        if solar_days != baseline_days:
            risk_flags.extend(["diagnostic_baseline_disagreement", "manual_review_recommended"])
        if confidence_score < 0.65:
            risk_flags.append("manual_review_recommended")
        if index + 1 in {5, 8, 11} and confidence_score < 0.85:
            risk_flags.append("historically_sensitive_month")
        final_months.append(final_days)
        all_risk_flags.update(risk_flags)
        details.append(
            {
                "month": index + 1,
                "month_name": BS_MONTH_NAMES[index],
                "final_days": final_days,
                "probability": probability,
                "confidence_score": confidence_score,
                "confidence_label": _confidence_label(confidence_score),
                "model_agreement": stacked_detail["model_agreement"],
                "risk_flags": sorted(set(risk_flags)),
                "computational_days": solar_days,
                "statistical_pattern_days": statistical_days,
                "diagnostic_baseline_days": baseline_days,
                "computational_probability": solar["probabilities"][index],
                "computational_model_agreement": solar["model_agreement"][index],
                "final_source": stacked_detail["final_source"],
            }
        )

    confidence_score = round(sum(row["confidence_score"] for row in details) / 12, 4)
    payload = {
        "bs_year": bs_year,
        "months": final_months,
        "month_details": details,
        "year_total": sum(final_months),
        "confidence_score": confidence_score,
        "confidence": _confidence_label(confidence_score),
        "risk_flags": sorted(all_risk_flags),
        "constraints": _constraint_checks(final_months),
        "method_version": METHOD_VERSION,
        "calibration_version": CALIBRATION_VERSION,
        "run_id": DEFAULT_RUN_ID,
        "model_family": "computational_solar_ingress",
        "model_subfamily": "solar_civil_plus_past_pattern_stack",
        "source": _computed_source_payload(bs_year),
        "computational_model_outputs": solar["model_outputs"],
        "legacy_model_output": {
            "model": "legacy_cycle_baseline_diagnostic",
            "model_family": "diagnostic_baseline_not_product_output",
            "months": baseline_months,
            "year_total": sum(baseline_months),
            "model_outputs": baseline_models,
            "note": (
                "This baseline is retained for disagreement/risk diagnostics only. "
                "Future month lengths are computed with the solar-ingress civil-decision model."
            ),
        },
        "model_agreement": "ensemble",
        "engine_components": [
            "verified_month_length_corpus",
            "solar_ingress_computational_model",
            "civil_date_rule_calibration",
            "past_only_statistical_pattern_model",
            "legacy_cycle_diagnostic_model",
            "probabilistic_confidence_scoring",
            "loan_contract_risk_adapter",
        ],
        "limits": {
            "known_static_lookup": corpus_range_label(),
            "prediction_range": f"{BS_MIN_YEAR}-{PREDICTION_MAX_YEAR} BS",
            "ephemeris_status": _ephemeris_status(),
            "publication_status": "computed_prediction_not_official",
        },
        "source_status": "computed_prediction",
        "publication_status": "computed_prediction_not_official",
        "legacy_publication_status": "not_official_publication",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    return apply_year_total_gate(payload)


def compute_year_live(bs_year: int) -> dict[str, Any]:
    _validate_year(bs_year)
    if is_known_year(bs_year) and bs_year <= 2083:
        return _known_year_payload(bs_year)
    return _future_year_payload(bs_year)


def predict_year(bs_year: int) -> dict[str, Any]:
    _validate_year(bs_year)
    if is_known_year(bs_year) and bs_year <= 2083:
        return _known_year_payload(bs_year)
    precomputed = get_precomputed_year(bs_year)
    if precomputed is not None:
        return precomputed
    if live_compute_enabled():
        return compute_year_live(bs_year)
    if is_known_year(bs_year):
        return _known_year_payload(bs_year)
    raise ValueError(
        "Future BS prediction is not precomputed for this year. "
        "Run scripts/precompute_future_bs_predictions.py or enable PARVA_FUTURE_BS_LIVE_COMPUTE=1."
    )
