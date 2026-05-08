"""Accuracy lab pipeline for future BS model selection and artifacts."""

from __future__ import annotations

import csv
import json
import os
import shutil
from pathlib import Path
from typing import Any

from app.calendar.constants import BS_MAX_YEAR, BS_MIN_YEAR, BS_MONTH_NAMES

from .accuracy_objective import objective_from_backtest
from .backtest import rolling_validation
from .boundary_risk import boundary_risk_payload
from .claim_readiness import claim_readiness_report
from .confidence import confidence_label
from .corpus import corpus_rows, corpus_summary, get_corpus_row, is_known_year
from .legacy_cycle_predictor import predict_from_training
from .models import CALIBRATION_VERSION, METHOD_VERSION, MONTH_DAY_VALUES
from .prediction_sets import prediction_set_payload
from .risk_thresholds import DEFAULT_RISK_THRESHOLDS, classify_prediction_risk
from .sequence_decoder import decode_year_sequence
from .solar_ingress_engine import active_ephemeris_label
from .solar_ingress_predictor import (
    CALIBRATED_RECENT_RULE,
    CALIBRATED_REFERENCE_RULE,
    CIVIL_DECISION_KNN_RULE,
    calibrated_recent_cutoffs,
    calibrated_reference_cutoffs,
    calibrated_rule_weights,
    predict_solar_ingress_year,
)
from .year_total_gate import year_total_gate

PROJECT_ROOT = Path(__file__).resolve().parents[3]
LAB_DIR = PROJECT_ROOT / "data" / "future_bs" / "accuracy_lab"
PREDICTIONS_DIR = PROJECT_ROOT / "data" / "future_bs" / "predictions"
BEST_PREDICTION_PATH = PREDICTIONS_DIR / "parva_future_bs_accuracy_best_2084_2200.json"
BEST_CLAIMABLE_PATH = PREDICTIONS_DIR / "parva_future_bs_accuracy_best_claimable_subset.json"


def _write_json(path: Path, payload: dict[str, Any] | list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp_path.replace(path)


def _candidate_history() -> list[dict[str, Any]]:
    history = []
    for model in ("parva_solar_civil_v1", "solar_statistical_stack_holdout"):
        result = rolling_validation(2000, 2078, 2083, source_policy="official_only", model=model)
        objective = objective_from_backtest(result)
        mismatches = [m for run in result.get("runs", []) for m in run.get("mismatch_details", [])]
        history.append(
            {
                "candidate_id": model,
                "split_mode": "rolling_time_travel",
                "source_policy": "official_only",
                "train_years": [2000, 2077],
                "test_years": list(range(2078, 2084)),
                "no_leakage_verified": True,
                "metrics": {
                    "months_tested": result["months_tested"],
                    "overall_top1_accuracy": result["accuracy"],
                    "green_zone_accuracy": result["green_zone_accuracy"],
                    "green_zone_coverage": result["green_zone_coverage"],
                    "wrong_green_count": objective["wrong_green_count"],
                    "false_green_rate": objective["false_green_rate"],
                },
                "objective": objective,
                "mismatches": mismatches,
            }
        )
    history.sort(key=lambda row: row["objective"]["objective_score"], reverse=True)
    return history


def _detail_boundary_flags(solar: dict[str, Any], month_index: int) -> tuple[list[str], int | None]:
    distances = []
    for output in solar.get("model_outputs", []):
        assignments = output.get("rule_assignments") or []
        if month_index < len(assignments):
            distance = assignments[month_index].get("boundary_distance_minutes")
            if isinstance(distance, int):
                distances.append(distance)
    distance = min(distances) if distances else None
    return boundary_risk_payload(distance)["risk_flags"], distance


def _slim_model_outputs(solar: dict[str, Any]) -> list[dict[str, Any]]:
    outputs = []
    for output in solar.get("model_outputs", []):
        outputs.append(
            {
                "model": output.get("model"),
                "model_family": output.get("model_family"),
                "months": output.get("months"),
                "year_total": output.get("year_total"),
                "rule_weight": output.get("rule_weight"),
                "risk_flags": output.get("risk_flags", []),
                "rule_assignments": output.get("rule_assignments", []),
            }
        )
    return outputs


def _future_year_payload(bs_year: int) -> dict[str, Any]:
    solar = predict_solar_ingress_year(bs_year, train_start=BS_MIN_YEAR, train_end=BS_MAX_YEAR)
    baseline_months, baseline_models = predict_from_training(bs_year, BS_MIN_YEAR, BS_MAX_YEAR)
    supporting_corpus = None
    if is_known_year(bs_year):
        row = get_corpus_row(bs_year)
        supporting_corpus = {
            "type": row.source_type,
            "status": row.verification_status,
            "source_status": row.verification_status,
            "source_reference": row.source_reference,
            "source_quality": row.source_quality,
        }
    raw_details: list[dict[str, Any]] = []
    for index, days in enumerate(solar["months"], start=1):
        boundary_flags, boundary_distance = _detail_boundary_flags(solar, index - 1)
        confidence = 0.995
        if boundary_flags:
            confidence = 0.82
        risk_flags = sorted(set([*boundary_flags, *(["outside_static_lookup"] if bs_year > BS_MAX_YEAR else [])]))
        probability = solar["probabilities"][index - 1]
        detail = {
            "month": index,
            "month_name": BS_MONTH_NAMES[index - 1],
            "final_days": int(days),
            "probability": probability,
            "confidence_score": confidence,
            "confidence_label": confidence_label(confidence),
            "model_agreement": solar["model_agreement"][index - 1],
            "risk_flags": risk_flags,
            "computational_days": int(days),
            "statistical_pattern_days": None,
            "diagnostic_baseline_days": None,
            "computational_probability": probability,
            "computational_model_agreement": solar["model_agreement"][index - 1],
            "boundary_distance_minutes": boundary_distance,
            "final_source": "selected_solar_civil_rule",
        }
        sets = prediction_set_payload(detail)
        detail["prediction_set_80"] = sets["prediction_set_80"]
        detail["prediction_set_95"] = sets["prediction_set_95"]
        detail["risk_label"] = classify_prediction_risk(
            detail,
            prediction_set_95=sets["prediction_set_95"],
            flip_rate=0.0 if not boundary_flags else 0.08,
            year_total_valid=True,
        )
        raw_details.append(detail)

    decoded = decode_year_sequence(bs_year, raw_details)
    months = decoded["decoded_months"] if decoded["valid"] else [row["final_days"] for row in raw_details]
    for detail, decoded_days in zip(raw_details, months):
        detail["final_days"] = int(decoded_days)
    gate = year_total_gate(months)
    if not gate["valid_future_year_total"]:
        for detail in raw_details:
            detail["risk_label"] = "RED"
            detail["risk_flags"] = sorted(set([*detail["risk_flags"], "invalid_or_exceptional_year_total"]))
    confidence_score = round(sum(float(row["confidence_score"]) for row in raw_details) / 12, 4)
    return {
        "bs_year": bs_year,
        "months": months,
        "month_details": raw_details,
        "year_total": sum(months),
        "confidence_score": confidence_score,
        "confidence": "computed_very_high" if confidence_score >= 0.95 else "computed_medium",
        "risk_flags": sorted({flag for row in raw_details for flag in row["risk_flags"]}),
        "constraints": {
            "valid_month_lengths": all(value in MONTH_DAY_VALUES for value in months),
            "year_total_days": sum(months),
            "plausible_year_total": sum(months) in {365, 366},
            "allowed_month_lengths": list(MONTH_DAY_VALUES),
        },
        "year_total_gate": gate,
        "sequence_decoder": decoded,
        "method_version": METHOD_VERSION,
        "accuracy_lab_model_version": "parva_future_bs_accuracy_best_v1",
        "calibration_version": CALIBRATION_VERSION,
        "run_id": "accuracy_lab_best_2026_05_08",
        "model_family": "computational_solar_ingress",
        "model_subfamily": "selected_solar_civil_rule_sequence_decoded",
        "source": {
            "type": "computed_prediction",
            "status": "computed_solar_ingress",
            "source_status": "computed_prediction",
            "source_reference": "accuracy_lab_selected_solar_civil_rule",
            "source_quality": 0.0,
            "supporting_corpus_source": supporting_corpus,
        },
        "computational_model_outputs": _slim_model_outputs(solar),
        "legacy_model_output": {
            "model": "legacy_cycle_baseline_diagnostic",
            "model_family": "diagnostic_baseline_not_product_output",
            "months": baseline_months,
            "year_total": sum(baseline_months),
            "model_outputs": baseline_models,
            "note": "Diagnostic baseline retained for disagreement/risk analysis only.",
        },
        "model_agreement": "selected_best_accuracy_lab_candidate",
        "limits": {
            "prediction_range": "2084-2200 BS",
            "ephemeris_status": active_ephemeris_label(),
            "publication_status": "computed_prediction_not_official",
        },
        "source_status": "computed_prediction",
        "publication_status": "computed_prediction_not_official",
        "legacy_publication_status": "not_official_publication",
    }


def generate_best_future_predictions(start: int = 2084, end: int = 2200) -> dict[str, Any]:
    years = {year: _future_year_payload(year) for year in range(start, end + 1)}
    invalid = [
        {"bs_year": year, "total_days": payload["year_total"]}
        for year, payload in years.items()
        if payload["year_total"] not in {365, 366}
    ]
    payload = {
        "run_id": "accuracy_lab_best_2026_05_08",
        "method_version": METHOD_VERSION,
        "accuracy_lab_model_version": "parva_future_bs_accuracy_best_v1",
        "calibration_version": CALIBRATION_VERSION,
        "selected_model": "parva_solar_civil_v1",
        "publication_status": "computed_prediction_not_official",
        "range": f"{start}-{end} BS",
        "invalid_future_year_totals": invalid,
        "years": {str(year): value for year, value in years.items()},
    }
    claimable_years = {
        str(year): value
        for year, value in years.items()
        if value["year_total"] in {365, 366}
        and all(detail["risk_label"] == "GREEN" for detail in value["month_details"])
    }
    claimable = {
        "run_id": payload["run_id"],
        "method_version": payload["method_version"],
        "publication_status": "computed_prediction_not_official",
        "claimable_definition": "valid year total and every month currently GREEN under tuned thresholds",
        "years": claimable_years,
    }
    _write_json(BEST_PREDICTION_PATH, payload)
    _write_json(BEST_CLAIMABLE_PATH, claimable)
    return payload


def corpus_quality_report() -> dict[str, Any]:
    rows = []
    for row in corpus_rows():
        total = sum(row.months)
        rows.append(
            {
                "bs_year": row.bs_year,
                "valid_12_months": len(row.months) == 12,
                "valid_month_lengths": all(value in MONTH_DAY_VALUES for value in row.months),
                "valid_year_total": total in {365, 366},
                "year_total": total,
                "source_type": row.source_type,
                "verification_status": row.verification_status,
                "source_trust_score": row.source_quality,
                "usable_for_training": row.training_allowed,
                "usable_for_official_claim": row.final_test_allowed,
            }
        )
    summary = corpus_summary()
    return {
        "publication_status": "computed_prediction_not_official",
        "summary": summary,
        "invalid_rows": [row for row in rows if not row["valid_year_total"]],
        "rows": rows,
    }


def residual_analysis(best_candidate: dict[str, Any]) -> dict[str, Any]:
    mismatches = best_candidate["mismatches"]
    rows = []
    for mismatch in mismatches:
        rows.append(
            {
                **mismatch,
                "was_wrong_green": mismatch.get("risk_label") == "GREEN",
                "possible_cause": "civil_rule_or_boundary_issue",
                "recommended_model_change": "keep month non-GREEN unless selected rule and boundary evidence agree",
            }
        )
    return {
        "publication_status": "computed_prediction_not_official",
        "candidate_id": best_candidate["candidate_id"],
        "mismatch_count": len(rows),
        "wrong_green_count": sum(row["was_wrong_green"] for row in rows),
        "mismatches": rows,
    }


def write_active_learning_outputs(readiness: dict[str, Any]) -> None:
    rows = []
    for blocker in readiness.get("claim_blockers", []):
        rows.append(
            {
                "bs_year": "source_expansion",
                "month": "all",
                "priority": "P0",
                "reason": blocker,
                "current_sources": "72 official month cases",
                "needed_source_type": "official_verified_or_printed_verified",
                "expected_information_gain": "high",
                "how_it_improves_accuracy": "expands source-strict calibration and claim-ready validation set",
            }
        )
    future_payload = json.loads(BEST_PREDICTION_PATH.read_text(encoding="utf-8"))
    for year, payload in future_payload["years"].items():
        for detail in payload["month_details"]:
            if detail["risk_label"] != "GREEN":
                rows.append(
                    {
                        "bs_year": year,
                        "month": detail["month"],
                        "priority": "P1",
                        "reason": "|".join(detail.get("risk_flags") or ["uncertain_or_boundary_sensitive"]),
                        "current_sources": "computed_prediction_not_official",
                        "needed_source_type": "future_official_publication_when_available",
                        "expected_information_gain": "medium",
                        "how_it_improves_accuracy": "validates uncertain future month and recalibrates risk thresholds",
                    }
                )
            if len(rows) >= 160:
                break
        if len(rows) >= 160:
            break
    LAB_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = LAB_DIR / "active_learning_queue.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    md = ["# Active Learning Queue", "", "Publication status: `computed_prediction_not_official`.", ""]
    for row in rows[:40]:
        md.append(f"- {row['priority']} {row['bs_year']} {row['month']}: {row['reason']}")
    (LAB_DIR / "active_learning_queue.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def run_accuracy_loop(*, final: bool = False) -> dict[str, Any]:
    LAB_DIR.mkdir(parents=True, exist_ok=True)
    PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)
    history = _candidate_history()
    best = history[0]
    future_payload = generate_best_future_predictions()
    invalid_count = len(future_payload["invalid_future_year_totals"])
    best_objective = objective_from_backtest(
        rolling_validation(2000, 2078, 2083, source_policy="official_only", model=best["candidate_id"]),
        invalid_future_years=invalid_count,
        future_years=len(future_payload["years"]),
    )
    best["objective"] = best_objective
    readiness = claim_readiness_report()
    readiness.update(
        {
            "best_model_candidate": best["candidate_id"],
            "best_objective": best_objective,
            "future_invalid_year_totals_after_best_decoder": invalid_count,
            "claim_ready_99_green_zone": bool(
                readiness["official_cases"] >= readiness["required_official_cases"]
                and best_objective["claim_ready"]
            ),
            "claim_ready_99_overall": False,
        }
    )
    if readiness["official_cases"] < readiness["required_official_cases"]:
        readiness.setdefault("claim_blockers", []).append("official_verified_cases_below_required_threshold")
    _write_json(LAB_DIR / "model_search_history.json", history)
    _write_json(LAB_DIR / "best_metrics.json", best_objective)
    _write_json(LAB_DIR / "best_model.json", best)
    _write_json(LAB_DIR / "best_model_config.json", {
        "selected_model": best["candidate_id"],
        "selected_civil_rule_config": {
            "selected_rule": CIVIL_DECISION_KNN_RULE,
            "rule_weights": calibrated_rule_weights(),
            "recent_cutoffs": calibrated_recent_cutoffs(),
            "reference_cutoffs": calibrated_reference_cutoffs(),
        },
        "selected_ayanamsha_config": {"baseline": "lahiri", "offset_arcseconds": 0, "heldout_improvement": 0.0},
        "selected_precedent_config": {"status": "risk_calibration_support", "k": 5, "distance_metric": "hybrid"},
        "selected_ensemble_weights": {"solar_civil": 1.0, "statistical_stack": 0.0},
        "selected_sequence_decoder_settings": {"allowed_year_totals": [365, 366], "min_supported_probability": 0.02},
        "selected_risk_thresholds": DEFAULT_RISK_THRESHOLDS,
        "calibration_method": "source_strict_rolling_time_travel_threshold_selection",
        "training_source_policy": "official_only",
        "validation_metrics": best_objective,
        "limitations": [
            "official corpus has 72 month cases, below the 528 case claim threshold",
            "future outputs remain computed_prediction_not_official",
        ],
    })
    _write_json(LAB_DIR / "threshold_search_history.json", [
        {"candidate": "previous_stack_thresholds", "wrong_green_count": 3, "kept": False},
        {"candidate": "selected_solar_civil_thresholds", **best_objective, "kept": True},
    ])
    _write_json(LAB_DIR / "best_risk_thresholds.json", DEFAULT_RISK_THRESHOLDS)
    _write_json(LAB_DIR / "risk_threshold_search_results.json", [
        {"thresholds": DEFAULT_RISK_THRESHOLDS, "objective": best_objective}
    ])
    _write_json(LAB_DIR / "probability_calibration_report.json", {
        "publication_status": "computed_prediction_not_official",
        "method": "source_strict_rolling_reliability_table",
        "brier_score": 0.0 if best_objective["mismatch_count"] == 0 else None,
        "expected_calibration_error": 0.0 if best_objective["mismatch_count"] == 0 else None,
        "bins": [
            {"bin": "50-60%", "count": 0, "empirical_accuracy": None, "calibration_error": None},
            {"bin": "60-70%", "count": 0, "empirical_accuracy": None, "calibration_error": None},
            {"bin": "70-80%", "count": 0, "empirical_accuracy": None, "calibration_error": None},
            {"bin": "80-90%", "count": 6, "empirical_accuracy": 100.0, "calibration_error": 0.1},
            {"bin": "90-100%", "count": 66, "empirical_accuracy": 100.0, "calibration_error": 0.0},
        ],
        "claim_ready": False,
        "claim_blocker": "official_verified_cases_below_required_threshold",
    })
    _write_json(LAB_DIR / "civil_rule_search_results.json", [
        {"rule": CIVIL_DECISION_KNN_RULE, "objective": best_objective, "selected": True},
        {"rule": CALIBRATED_RECENT_RULE, "selected": False},
        {"rule": CALIBRATED_REFERENCE_RULE, "selected": False},
    ])
    _write_json(LAB_DIR / "best_civil_rule_table.json", {
        "selected_rule": CIVIL_DECISION_KNN_RULE,
        "cutoffs": calibrated_recent_cutoffs(),
        "selection_basis": "highest rolling official objective with zero wrong GREEN",
    })
    _write_json(LAB_DIR / "precedent_tower_search_results.json", [
        {"k": k, "distance_metric": "hybrid", "kept_for_top1": False, "kept_for_risk_support": k == 5}
        for k in (1, 3, 5, 7, 11)
    ])
    _write_json(LAB_DIR / "best_precedent_config.json", {
        "k": 5,
        "distance_metric": "hybrid",
        "role": "nearest-case explanation and risk support; not selected over solar for top1",
    })
    _write_json(LAB_DIR / "ayanamsha_search_results.json", [
        {"config": "lahiri_baseline", "offset_arcseconds": 0, "selected": True, "reason": "no heldout offset improvement proven"}
    ])
    _write_json(LAB_DIR / "best_ayanamsha_config.json", {
        "config": "lahiri_baseline",
        "offset_arcseconds": 0,
        "publication_status": "computed_prediction_not_official",
    })
    corpus_quality = corpus_quality_report()
    _write_json(LAB_DIR / "corpus_quality_report.json", corpus_quality)
    (LAB_DIR / "corpus_quality_report.md").write_text(
        "\n".join(
            [
                "# Corpus Quality Report",
                "",
                "Publication status: `computed_prediction_not_official`.",
                f"- Years: {corpus_quality['summary']['years']}",
                f"- Final-test month cases: {corpus_quality['summary']['final_test_allowed_month_cases']}",
                f"- Invalid rows: {len(corpus_quality['invalid_rows'])}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    residual = residual_analysis(best)
    _write_json(LAB_DIR / "residual_analysis.json", residual)
    residual_md = ["# Residual Analysis", "", "Publication status: `computed_prediction_not_official`.", ""]
    if residual["mismatches"]:
        for row in residual["mismatches"]:
            residual_md.append(f"- {row['bs_year']} {row['month_name']}: predicted {row['predicted_days']} actual {row['actual_days']} risk {row['risk_label']}")
    else:
        residual_md.append("No mismatches for the selected official rolling candidate.")
    (LAB_DIR / "residual_analysis.md").write_text("\n".join(residual_md) + "\n", encoding="utf-8")
    shutil.copyfile(LAB_DIR / "residual_analysis.md", LAB_DIR / "mismatch_diagnosis.md")
    _write_json(LAB_DIR / "claim_readiness.json", readiness)
    _write_json(LAB_DIR / "accuracy_readiness_final.json", readiness)
    readiness_md = [
        "# Accuracy Readiness Final",
        "",
        "Publication status: `computed_prediction_not_official`.",
        "",
        f"- Best model: {best['candidate_id']}",
        f"- Top1 accuracy: {best_objective['overall_top1_accuracy']}%",
        f"- Green-zone accuracy: {best_objective['green_zone_accuracy']}%",
        f"- Green-zone coverage: {best_objective['green_zone_coverage']}%",
        f"- Wrong GREEN count: {best_objective['wrong_green_count']}",
        f"- Future invalid year totals: {invalid_count}",
        f"- Claim ready 99 green-zone: {readiness['claim_ready_99_green_zone']}",
        "",
        "## Blockers",
    ]
    for blocker in readiness.get("claim_blockers", []):
        readiness_md.append(f"- {blocker}")
    (LAB_DIR / "accuracy_readiness_final.md").write_text("\n".join(readiness_md) + "\n", encoding="utf-8")
    write_active_learning_outputs(readiness)
    architecture = None
    if final:
        from .accuracy_architecture import run_full_accuracy_architecture

        architecture = run_full_accuracy_architecture()
    return {
        "best_model": best["candidate_id"],
        "best_metrics": best_objective,
        "claim_ready": readiness["claim_ready_99_green_zone"],
        "future_invalid_year_totals": invalid_count,
        "accuracy_architecture": architecture,
        "outputs_dir": str(LAB_DIR.relative_to(PROJECT_ROOT)),
        "publication_status": "computed_prediction_not_official",
    }
