"""Future BS month-length prediction, comparison, and loan-impact services."""

from __future__ import annotations

from typing import Any

from app.calendar.constants import BS_MONTH_NAMES
from app.future_bs.backtest import backtest_model as computational_backtest_model
from app.future_bs.backtest import full_replay_backtest, rolling_validation
from app.future_bs.boundary_risk import boundary_risk_payload
from app.future_bs.compare import compare_external_sheet as future_compare_external_sheet
from app.future_bs.compare import external_year_map as future_external_year_map
from app.future_bs.corpus import corpus_summary
from app.future_bs.ensemble import CALIBRATION_VERSION, METHOD_VERSION
from app.future_bs.ensemble import predict_year as future_predict_year
from app.future_bs.excel_importer import import_month_lengths_base64
from app.future_bs.explain import explain_prediction_month
from app.future_bs.exports import predictions_to_csv as future_predictions_to_csv
from app.future_bs.exports import predictions_to_xlsx as future_predictions_to_xlsx
from app.future_bs.loan_impact import simulate_loan_impact as future_simulate_loan_impact
from app.future_bs.model_registry import model_registry_payload
from app.future_bs.models import PREDICTION_MAX_YEAR
from app.future_bs.precomputed_store import precomputed_store_status
from app.future_bs.residual_analysis import residual_summary
from app.future_bs.run_registry import get_model_run, list_model_runs
from app.future_bs.source_registry import load_source_registry


def _validate_month(month: int) -> None:
    if month < 1 or month > 12:
        raise ValueError("month must be between 1 and 12.")


def predict_bs_year(bs_year: int) -> dict[str, Any]:
    return future_predict_year(bs_year)


def predict_bs_range(start: int, end: int) -> dict[str, Any]:
    if start > end:
        raise ValueError("start must be less than or equal to end.")
    if end - start > 200:
        raise ValueError("Range requests are limited to 201 BS years.")
    years = [predict_bs_year(year) for year in range(start, end + 1)]
    return {
        "start": start,
        "end": end,
        "total_years": len(years),
        "years": years,
        "method_version": METHOD_VERSION,
    }


def _external_year_map(years: list[dict[str, Any]]) -> dict[int, list[int]]:
    return future_external_year_map(years)


def compare_external_sheet(source_name: str, years: list[dict[str, Any]]) -> dict[str, Any]:
    return future_compare_external_sheet(source_name, years, predict_fn=predict_bs_year)


def backtest_model(train_start: int, train_end: int, test_start: int, test_end: int) -> dict[str, Any]:
    return computational_backtest_model(train_start, train_end, test_start, test_end)


def future_bs_capabilities_payload() -> dict[str, Any]:
    registry = model_registry_payload()
    jpl_available = any(
        adapter.get("name") == "jpl_de440" and adapter.get("available")
        for adapter in registry.get("ephemeris_adapters", [])
    )
    not_claimed = [
        "official_future_publication",
        "legal_or_tax_final_authority",
    ]
    if not jpl_available:
        not_claimed.append("DE440 production certification until a kernel is configured")
    return {
        "surface": "future_bs_month_length_validation",
        "status": "evaluation_ready",
        "core_product": "BS year -> 12 month lengths -> confidence -> mismatch report -> loan impact",
        "stable": [
            "source_labeled_corpus",
            "precomputed_future_predictions",
            "probabilistic_future_month_length_prediction",
            "external_sheet_comparison",
            "month_level_explainability",
            "loan_interest_impact_simulation",
            "csv_export",
            "xlsx_export",
            "immutable_model_runs",
        ],
        "computed": [
            "future_month_lengths_beyond_static_lookup",
            "confidence_scores",
            "boundary_risk_flags",
            "backtest_metrics",
            "residual_analysis",
        ],
        "not_claimed": not_claimed,
        "method_version": METHOD_VERSION,
        "calibration_version": CALIBRATION_VERSION,
        "corpus": corpus_summary(),
        "precomputed_store": precomputed_store_status(),
        "model_registry": registry,
        "source_registry": load_source_registry(),
        "recommended_use": [
            "technical validation",
            "InfoDevelopers Excel comparison",
            "loan-contract calendar-risk screening",
            "manual-review prioritization",
        ],
    }


def full_backtest(start: int, end: int) -> dict[str, Any]:
    return full_replay_backtest(start, end)


def rolling_backtest(train_start: int, test_start: int, test_end: int) -> dict[str, Any]:
    return rolling_validation(train_start, test_start, test_end)


def backtest_residuals(train_start: int, train_end: int, test_start: int, test_end: int) -> dict[str, Any]:
    return residual_summary(train_start, train_end, test_start, test_end)


def explain_month(year: int, month: int) -> dict[str, Any]:
    _validate_month(month)
    prediction = predict_bs_year(year)
    detail = prediction["month_details"][month - 1]
    explanation = explain_prediction_month(prediction, month)
    return {
        "bs_year": year,
        "month": month,
        "month_name": BS_MONTH_NAMES[month - 1],
        "final_days": detail["final_days"],
        "probability": detail["probability"],
        "confidence": detail["confidence_label"],
        "confidence_score": detail["confidence_score"],
        "model_agreement": detail["model_agreement"],
        "risk_flags": detail["risk_flags"],
        "model_outputs": prediction.get("computational_model_outputs") or [],
        "computational_model_outputs": prediction.get("computational_model_outputs") or [],
        "legacy_model_output": prediction.get("legacy_model_output"),
        "computational_days": detail.get("computational_days"),
        "legacy_days": detail.get("legacy_days"),
        "reasoning": explanation["reasoning"],
        "recommendation": explanation["recommendation"],
        "interpretation": _interpret_month_risk(detail),
        "method_version": METHOD_VERSION,
    }


def boundary_risk(year: int, month: int) -> dict[str, Any]:
    _validate_month(month)
    prediction = predict_bs_year(year)
    detail = prediction["month_details"][month - 1]
    distances: list[int] = []
    for model in prediction.get("computational_model_outputs") or []:
        assignments = model.get("rule_assignments") or []
        if month - 1 < len(assignments):
            distance = assignments[month - 1].get("boundary_distance_minutes")
            if isinstance(distance, int):
                distances.append(distance)
    distance = min(distances) if distances else None
    payload = boundary_risk_payload(distance)
    payload.update(
        {
            "bs_year": year,
            "month": month,
            "month_name": BS_MONTH_NAMES[month - 1],
            "final_days": detail["final_days"],
            "method_version": METHOD_VERSION,
        }
    )
    return payload


def import_excel_and_compare(source_name: str, content_base64: str, file_format: str) -> dict[str, Any]:
    years = import_month_lengths_base64(content_base64, file_format)
    comparison = compare_external_sheet(source_name, years)
    return {
        "imported_years": len(years),
        "comparison": comparison,
    }


def model_runs() -> list[dict[str, Any]]:
    return list_model_runs()


def model_run(run_id: str) -> dict[str, Any]:
    return get_model_run(run_id)


def _interpret_month_risk(detail: dict[str, Any]) -> str:
    if "manual_review_recommended" in detail["risk_flags"]:
        return "Do not use this month in long-term loan contracts without manual review."
    if "model_disagreement" in detail["risk_flags"]:
        return "The computational and legacy fallback models disagree; treat this month as reviewable."
    if detail["confidence_label"] == "official_verified":
        return "Known structured corpus year, not a future computed prediction."
    return "Prediction is internally consistent under the current solar-ingress calibrated ensemble."


def simulate_loan_impact(payload: dict[str, Any]) -> dict[str, Any]:
    return future_simulate_loan_impact(payload, predict_fn=predict_bs_year)


def predictions_to_csv(start: int, end: int) -> str:
    return future_predictions_to_csv(start, end, range_fn=predict_bs_range)


def predictions_to_xlsx(start: int, end: int) -> bytes:
    return future_predictions_to_xlsx(start, end, range_fn=predict_bs_range)


__all__ = [
    "CALIBRATION_VERSION",
    "METHOD_VERSION",
    "PREDICTION_MAX_YEAR",
    "backtest_model",
    "backtest_residuals",
    "boundary_risk",
    "compare_external_sheet",
    "explain_month",
    "full_backtest",
    "future_bs_capabilities_payload",
    "import_excel_and_compare",
    "model_run",
    "model_runs",
    "predict_bs_range",
    "predict_bs_year",
    "predictions_to_csv",
    "predictions_to_xlsx",
    "rolling_backtest",
    "simulate_loan_impact",
]
