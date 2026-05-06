"""Solar-ingress plus legacy-cycle future BS prediction ensemble."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any

from app.calendar.constants import BS_MAX_YEAR, BS_MIN_YEAR, BS_MONTH_NAMES
from app.calendar.provenance import get_bs_year_provenance

from .corpus import corpus_range_label, is_known_year, known_months, source_label_for_year
from .legacy_cycle_predictor import predict_legacy_cycle
from .models import CALIBRATION_VERSION, METHOD_VERSION, MONTH_DAY_VALUES, PREDICTION_MAX_YEAR
from .solar_ingress_predictor import predict_solar_ingress_year


def _validate_year(bs_year: int) -> None:
    if bs_year < BS_MIN_YEAR or bs_year > PREDICTION_MAX_YEAR:
        raise ValueError(
            f"BS year {bs_year} is outside the future-BS engine range "
            f"({BS_MIN_YEAR}-{PREDICTION_MAX_YEAR})."
        )


def _confidence_label(score: float, *, known_official: bool = False) -> str:
    if known_official:
        return "official_verified"
    if score >= 0.95:
        return "computed_very_high"
    if score >= 0.85:
        return "computed_high"
    if score >= 0.70:
        return "computed_medium"
    if score >= 0.55:
        return "computed_low"
    return "needs_review"


def _horizon_factor(bs_year: int) -> float:
    if bs_year <= BS_MAX_YEAR:
        return 1.0
    distance = bs_year - BS_MAX_YEAR
    if distance <= 10:
        return 0.94
    if distance <= 25:
        return 0.88
    if distance <= 50:
        return 0.80
    if distance <= 75:
        return 0.72
    return 0.62


def _constraint_checks(months: list[int]) -> dict[str, Any]:
    total_days = sum(months)
    return {
        "valid_month_lengths": all(days in MONTH_DAY_VALUES for days in months),
        "year_total_days": total_days,
        "plausible_year_total": 354 <= total_days <= 368,
        "allowed_month_lengths": list(MONTH_DAY_VALUES),
    }


def _source_payload(bs_year: int) -> dict[str, Any]:
    provenance = get_bs_year_provenance(bs_year)
    return {
        "type": source_label_for_year(bs_year) if is_known_year(bs_year) else "computed_prediction",
        "status": provenance.source_status,
        "structured_official_range": provenance.official_structured_range,
        "static_lookup_range": provenance.static_lookup_range,
        "note": provenance.note,
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
            "ephemeris_status": "swiss_moshier_lahiri_sidereal",
            "publication_status": "not_official_publication",
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _future_year_payload(bs_year: int) -> dict[str, Any]:
    solar = predict_solar_ingress_year(bs_year)
    legacy = predict_legacy_cycle(bs_year)
    horizon = _horizon_factor(bs_year)
    details = []
    final_months: list[int] = []
    all_risk_flags = set(solar["risk_flags"])
    all_risk_flags.add("outside_static_lookup")
    if bs_year > BS_MAX_YEAR + 50:
        all_risk_flags.add("long_horizon")

    for index in range(12):
        solar_days = solar["months"][index]
        legacy_days = legacy.months[index]
        votes: Counter[int] = Counter()
        votes[solar_days] += 1.0
        votes[legacy_days] += legacy.weight
        final_days = votes.most_common(1)[0][0]
        total_weight = sum(votes.values()) or 1.0
        probability = {
            f"{days}_days": round(votes.get(days, 0.0) / total_weight, 4)
            for days in MONTH_DAY_VALUES
        }
        confidence_score = round(max(probability.values()) * horizon, 4)
        risk_flags = []
        if bs_year > BS_MAX_YEAR:
            risk_flags.append("outside_static_lookup")
        if bs_year > BS_MAX_YEAR + 50:
            risk_flags.append("long_horizon")
        if solar_days != legacy_days:
            risk_flags.extend(["model_disagreement", "manual_review_recommended"])
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
                "model_agreement": "2/2" if solar_days == legacy_days else "1/2",
                "risk_flags": sorted(set(risk_flags)),
                "computational_days": solar_days,
                "legacy_days": legacy_days,
                "computational_probability": solar["probabilities"][index],
                "computational_model_agreement": solar["model_agreement"][index],
            }
        )

    confidence_score = round(sum(row["confidence_score"] for row in details) / 12, 4)
    return {
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
        "model_family": "computational_solar_ingress",
        "source": _source_payload(bs_year),
        "computational_model_outputs": solar["model_outputs"],
        "legacy_model_output": legacy.payload(),
        "model_agreement": "ensemble",
        "engine_components": [
            "verified_month_length_corpus",
            "solar_ingress_computational_model",
            "civil_date_rule_calibration",
            "legacy_cycle_fallback_model",
            "probabilistic_confidence_scoring",
            "loan_contract_risk_adapter",
        ],
        "limits": {
            "known_static_lookup": corpus_range_label(),
            "prediction_range": f"{BS_MIN_YEAR}-{PREDICTION_MAX_YEAR} BS",
            "ephemeris_status": "swiss_moshier_lahiri_sidereal",
            "publication_status": "not_official_publication",
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def predict_year(bs_year: int) -> dict[str, Any]:
    _validate_year(bs_year)
    if is_known_year(bs_year):
        return _known_year_payload(bs_year)
    return _future_year_payload(bs_year)
