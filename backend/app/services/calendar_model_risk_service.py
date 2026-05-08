"""Calendar model-risk service layer built on the future-BS engine."""

from __future__ import annotations

from typing import Any

from app.calendar.constants import BS_MONTH_NAMES
from app.future_bs.calendar_var import calendar_var_payload
from app.future_bs.claim_readiness import claim_readiness_report
from app.future_bs.committee_rule_posterior import committee_rule_posterior
from app.future_bs.models import CALIBRATION_VERSION, METHOD_VERSION
from app.future_bs.perturbation_robustness import perturbation_payload
from app.future_bs.precedent_tower import precedent_tower
from app.future_bs.prediction_sets import prediction_set_payload
from app.future_bs.red_team_2083 import replay_2083_ashwin
from app.future_bs.risk_thresholds import classify_prediction_risk
from app.future_bs.year_total_reconciliation import reconcile_year_total
from app.services.future_bs_service import (
    compare_external_sheet,
    predict_bs_year,
    simulate_loan_impact,
)


def _month_prediction(year: int, month: int) -> tuple[dict[str, Any], dict[str, Any]]:
    if month < 1 or month > 12:
        raise ValueError("month must be between 1 and 12.")
    prediction = predict_bs_year(year)
    return prediction, prediction["month_details"][month - 1]


def _risk_label(
    detail: dict[str, Any],
    year_gate: dict[str, Any] | None = None,
    *,
    prediction_set_95: list[int] | None = None,
    flip_rate: float = 0.0,
) -> str:
    if year_gate and not year_gate.get("valid_future_year_total", True):
        return "RED"
    return classify_prediction_risk(
        detail,
        prediction_set_95=prediction_set_95,
        flip_rate=flip_rate,
        year_total_valid=not year_gate or bool(year_gate.get("valid_future_year_total", True)),
    )


def prediction_payload(year: int, month: int) -> dict[str, Any]:
    prediction, detail = _month_prediction(year, month)
    committee = committee_posterior_payload(year, month)
    precedent = precedent_tower(year, month)
    sets = prediction_set_payload(detail)
    perturbation = perturbation_payload(detail, committee=committee, precedent=precedent)
    risk_label = _risk_label(
        detail,
        prediction.get("year_total_gate"),
        prediction_set_95=sets["prediction_set_95"],
        flip_rate=float(perturbation["flip_rate"]),
    )
    return {
        "bs_year": year,
        "month": BS_MONTH_NAMES[month - 1].lower(),
        "month_number": month,
        "predicted_days": detail["final_days"],
        "publication_status": "computed_prediction_not_official",
        **sets,
        "risk_label": risk_label,
        "risk_reasons": detail.get("risk_flags", []),
        "physics_tower": {
            "predicted_days": detail.get("computational_days", detail["final_days"]),
            "confidence": detail.get("confidence_score"),
        },
        "precedent_tower": precedent,
        "committee_model": committee,
        "perturbation_robustness": perturbation,
        "calendar_var": {
            "one_day_mismatch_impact_available": True,
            "recommended_policy": (
                "override_ready_until_official_publication"
                if risk_label != "GREEN" or not perturbation["stable"]
                else "normal_computed_schedule_with_reconciliation_marker"
            ),
        },
        "year_total_gate": prediction.get("year_total_gate"),
        "year_total_reconciliation": reconcile_year_total(prediction),
        "metadata": {
            "run_id": prediction.get("run_id"),
            "model_version": METHOD_VERSION,
            "calibration_version": CALIBRATION_VERSION,
            "publication_status": "computed_prediction_not_official",
            "served_from": prediction.get("served_from", "computed_or_known_engine"),
        },
    }


def committee_posterior_payload(year: int, month: int) -> dict[str, Any]:
    prediction, detail = _month_prediction(year, month)
    posterior = committee_rule_posterior(year, month)
    method_risk = posterior["method_regime_risk"]
    if _risk_label(detail, prediction.get("year_total_gate")) == "RED":
        method_risk = "high"
    return {
        "bs_year": year,
        "month": month,
        "rule_entropy": posterior["rule_entropy"],
        "committee_rule_posterior": posterior["committee_rule_posterior"],
        "method_regime_risk": method_risk,
        "evidence": posterior["evidence"],
        "publication_status": "computed_prediction_not_official",
    }


def prediction_set_response(year: int, month: int) -> dict[str, Any]:
    _, detail = _month_prediction(year, month)
    return {
        "bs_year": year,
        "month": month,
        **prediction_set_payload(detail),
        "publication_status": "computed_prediction_not_official",
    }


def perturbation_response(year: int, month: int) -> dict[str, Any]:
    _, detail = _month_prediction(year, month)
    committee = committee_posterior_payload(year, month)
    precedent = precedent_tower(year, month)
    return {
        "bs_year": year,
        "month": month,
        **perturbation_payload(detail, committee=committee, precedent=precedent),
        "publication_status": "computed_prediction_not_official",
    }


def calendar_var_response(payload: dict[str, Any]) -> dict[str, Any]:
    year = int(payload["bs_year"])
    prediction = predict_bs_year(year)
    result = calendar_var_payload(payload, prediction=prediction)
    result["publication_status"] = "computed_prediction_not_official"
    return result


def stress_test_response(payload: dict[str, Any]) -> dict[str, Any]:
    var = calendar_var_response(payload)
    return {
        "scenario_count": len(var["stress_scenarios"]),
        "scenarios": var["stress_scenarios"],
        "calendar_var": var,
        "recommended_policy": var["recommended_policy"],
        "publication_status": "computed_prediction_not_official",
    }


def audit_external_sheet_response(payload: dict[str, Any]) -> dict[str, Any]:
    comparison = compare_external_sheet(
        payload.get("source_name", "external_sheet"),
        payload.get("years", []),
    )
    comparison["publication_status"] = "computed_prediction_not_official"
    comparison["report_sections"] = [
        "executive_summary",
        "agreement_rate",
        "high_confidence_disagreements",
        "boundary_sensitive_months",
        "financially_critical_mismatches",
        "model_metadata",
    ]
    return comparison


def capabilities_payload() -> dict[str, Any]:
    return {
        "surface": "future_bs_risk_research",
        "status": "research_preview",
        "publication_status": "computed_prediction_not_official",
        "public_surface": [
            "methodology_summary",
            "source_policy_summary",
            "claim_boundary",
            "aggregate_validation_posture",
            "risk_label_taxonomy",
        ],
        "private_deployment_surfaces": [
            "external_sheet_comparison",
            "aggregate audit report",
            "future month-length risk review",
            "schedule impact screening",
        ],
        "not_claimed": [
            "official_future_publication",
            "legal_or_tax_final_authority",
            "guaranteed_future_calendar_accuracy",
        ],
    }


def loan_impact_model_risk_response(payload: dict[str, Any]) -> dict[str, Any]:
    result = simulate_loan_impact(payload)
    result["publication_status"] = "computed_prediction_not_official"
    return result


__all__ = [
    "audit_external_sheet_response",
    "calendar_var_response",
    "capabilities_payload",
    "claim_readiness_report",
    "committee_posterior_payload",
    "loan_impact_model_risk_response",
    "perturbation_response",
    "prediction_payload",
    "prediction_set_response",
    "replay_2083_ashwin",
    "stress_test_response",
]
