#!/usr/bin/env python3
"""Build the curated public Future BS snapshot from the selected research run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESEARCH_ROOT = PROJECT_ROOT / "data" / "future_bs"
PREDICTION_SOURCE = RESEARCH_ROOT / "predictions" / "parva_future_bs_accuracy_best_2084_2200.json"
METRICS_SOURCE = RESEARCH_ROOT / "accuracy_lab" / "unified_rolling_validation.json"
PUBLIC_DIR = RESEARCH_ROOT / "public"
FORECAST_OUTPUT = PUBLIC_DIR / "forecast_snapshot_v7_2084_2200.json"
MODEL_OUTPUT = PUBLIC_DIR / "selected_model_v7.json"
PUBLICATION_STATUS = "computed_prediction_not_official"


def _read(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Missing research source artifact: {path.relative_to(PROJECT_ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def _validation_payload(metrics: dict[str, Any]) -> dict[str, Any]:
    if not metrics.get("leakage_safe"):
        raise SystemExit("Selected validation artifact is not leakage-safe.")
    return {
        "official_rolling_time_travel": {
            "bs_year_range": "2078-2083",
            "exact_month_matches": int(metrics["exact_matches"]),
            "month_cases": int(metrics["months_tested"]),
            "accuracy": float(metrics["accuracy"]),
            "evaluation_kind": "rolling_past_only_official_evaluation",
            "training_source_policy": str(metrics["training_source_policy"]),
            "evaluation_source_policy": str(metrics["evaluation_source_policy"]),
            "leakage_safe": True,
        },
        "independent_broad_accuracy_claim_ready": False,
        "required_verified_month_cases_for_broad_claim": 528,
        "claim_boundary": (
            "The 72-case official window is a chronological rolling evaluation, but it remains "
            "too small for a broad future-accuracy guarantee."
        ),
    }


def _compact_month(detail: dict[str, Any]) -> dict[str, Any]:
    predicted_days = int(detail["final_days"])
    prediction_set_95 = [int(value) for value in detail.get("prediction_set_95") or [predicted_days]]
    if predicted_days not in prediction_set_95:
        raise SystemExit(
            f"Predicted value {predicted_days} is missing from the 95% model set for month {detail['month']}."
        )
    return {
        "month": int(detail["month"]),
        "month_name": str(detail["month_name"]),
        "predicted_days": predicted_days,
        "prediction_set_80": [
            int(value) for value in detail.get("prediction_set_80") or [predicted_days]
        ],
        "prediction_set_95": prediction_set_95,
        "model_support": {
            str(key): round(float(value), 6)
            for key, value in (detail.get("probability") or {}).items()
        },
        "heuristic_confidence_score": round(float(detail["confidence_score"]), 4),
        "confidence_label": str(detail["confidence_label"]),
        "model_agreement": str(detail["model_agreement"]),
        "boundary_distance_minutes": (
            int(detail["boundary_distance_minutes"])
            if detail.get("boundary_distance_minutes") is not None
            else None
        ),
        "risk_label": str(detail["risk_label"]).upper(),
        "risk_flags": sorted({str(flag) for flag in detail.get("risk_flags") or []}),
    }


def _compact_year(bs_year: int, payload: dict[str, Any]) -> dict[str, Any]:
    month_lengths = [int(value) for value in payload["months"]]
    months = [_compact_month(detail) for detail in payload["month_details"]]
    year_total = sum(month_lengths)
    if len(month_lengths) != 12 or len(months) != 12:
        raise SystemExit(f"BS {bs_year} must contain exactly 12 months.")
    if year_total not in {365, 366}:
        raise SystemExit(f"BS {bs_year} has invalid public year total {year_total}.")
    if [month["predicted_days"] for month in months] != month_lengths:
        raise SystemExit(f"BS {bs_year} month detail values do not match the year vector.")
    return {
        "bs_year": bs_year,
        "month_lengths": month_lengths,
        "months": months,
        "year_total_days": year_total,
        "heuristic_confidence_score": round(float(payload["confidence_score"]), 4),
        "confidence_label": str(payload["confidence"]),
        "risk_flags": sorted({str(flag) for flag in payload.get("risk_flags") or []}),
        "constraints": {
            "valid_month_lengths": all(29 <= value <= 32 for value in month_lengths),
            "valid_year_total": True,
            "allowed_month_lengths": [29, 30, 31, 32],
            "allowed_year_totals": [365, 366],
        },
        "model_family": str(payload["model_family"]),
        "model_subfamily": str(payload.get("model_subfamily") or "selected_research_model"),
    }


def main() -> int:
    predictions = _read(PREDICTION_SOURCE)
    metrics = _read(METRICS_SOURCE)
    if predictions.get("publication_status") != PUBLICATION_STATUS:
        raise SystemExit("Selected prediction source has an unsafe publication status.")

    source_years = predictions.get("years") or {}
    ordered_years = sorted(int(year) for year in source_years)
    if ordered_years != list(range(2084, 2201)):
        raise SystemExit("Selected prediction source must cover every BS year from 2084 through 2200.")

    validation = _validation_payload(metrics)
    model_id = str(predictions["selected_model"])
    methodology = {
        "schema_version": "1.1",
        "model_id": model_id,
        "method_version": str(predictions["method_version"]),
        "calibration_version": str(source_years["2084"]["calibration_version"]),
        "maturity": "research_preview",
        "publication_status": PUBLICATION_STATUS,
        "forecast_range": {"start_bs_year": 2084, "end_bs_year": 2200},
        "pipeline": [
            "source_labeled_bs_month_boundaries",
            "sidereal_solar_ingress_solving",
            "separate_reference_and_authority_training_towers",
            "minimum_authority_support_gate",
            "source_stratified_month_start_reconciliation",
            "year_sequence_decoding",
            "prediction_sets_and_boundary_risk",
        ],
        "selected_model": {
            "family": "authority_aware_solar_civil_ensemble",
            "subfamily": "source_stratified_month_start_reconciliation",
            "reference_source_policy": "all_reference",
            "authority_source_policy": "official_only",
            "minimum_authority_years": 4,
            "tower_weighting": "equal_total_weight_with_authority_tie_break",
            "physical_astronomy": "JPL/Swiss sidereal ingress evidence",
            "probability_semantics": "normalized_model_support_not_calibrated_probability",
        },
        "training": {
            "start_bs_year": 2000,
            "cutoff_bs_year": int(predictions["training_cutoff_bs_year"]),
            "past_only": True,
            "target_and_future_rows_excluded": True,
        },
        "authority_context": {
            "role": "Published civil decisions calibrate the authority tower; Parva does not replace NPNS.",
            "npns_2082_panchanga": "https://npns.gov.np/pages/the-year-of-2082-bs-3/",
            "npns_method_notice": "https://npns.gov.np/content/13/press-release-20251216/",
            "method_boundary": (
                "Recent NPNS material identifies traditional Saurukta Panchanga practice. "
                "The model therefore keeps modern physical ingress and published civil decisions separate."
            ),
        },
        "sequence_constraints": {
            "month_count": 12,
            "allowed_month_lengths": [29, 30, 31, 32],
            "allowed_year_totals": [365, 366],
        },
        "risk_policy": {
            "labels": ["GREEN", "YELLOW", "RED"],
            "prediction_sets": ["prediction_set_80", "prediction_set_95"],
            "prediction_set_semantics": "model_support_sets_without_calibrated_coverage",
            "boundary_distance_unit": "minutes",
            "review_required_for_every_public_forecast": True,
        },
        "validation": validation,
    }

    snapshot = {
        "schema_version": "1.1",
        "snapshot_id": "parva_future_bs_public_v7_2084_2200",
        "source_run_id": str(predictions["run_id"]),
        "model_id": model_id,
        "method_version": str(predictions["method_version"]),
        "calibration_version": methodology["calibration_version"],
        "maturity": "research_preview",
        "publication_status": PUBLICATION_STATUS,
        "forecast_range": {"start_bs_year": 2084, "end_bs_year": 2200},
        "validation": validation,
        "years": {
            str(year): _compact_year(year, source_years[str(year)])
            for year in ordered_years
        },
    }

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_OUTPUT.write_text(json.dumps(methodology, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    FORECAST_OUTPUT.write_text(json.dumps(snapshot, separators=(",", ":"), ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "model": str(MODEL_OUTPUT.relative_to(PROJECT_ROOT)),
                "forecast": str(FORECAST_OUTPUT.relative_to(PROJECT_ROOT)),
                "years": len(ordered_years),
                "publication_status": PUBLICATION_STATUS,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
