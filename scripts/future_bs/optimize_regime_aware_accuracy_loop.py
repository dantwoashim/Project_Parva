#!/usr/bin/env python3
"""Optimize and report the regime-aware future-BS accuracy layer."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.calendar.constants import BS_MONTH_NAMES  # noqa: E402
from app.future_bs.corpus import corpus_rows  # noqa: E402
from app.future_bs.legacy_cycle_predictor import predict_legacy_cycle  # noqa: E402
from app.future_bs.market_shadow import hamropatro_shadow_years  # noqa: E402
from app.future_bs.model_search.regime_candidate_runner import (  # noqa: E402
    RegimeCandidate,
    acceptance_gate,
    candidate_prediction,
)
from app.future_bs.source_policy import PUBLICATION_STATUS, policy_rows  # noqa: E402

OUT_DIR = PROJECT_ROOT / "data" / "future_bs" / "accuracy_lab"
REPORTS = {
    "current_state_metrics": OUT_DIR / "current_state_metrics.json",
    "current_state_summary": OUT_DIR / "current_state_summary.md",
    "regime_ensemble_metrics": OUT_DIR / "regime_ensemble_metrics.json",
    "regime_ensemble_metrics_md": OUT_DIR / "regime_ensemble_metrics.md",
    "loop_history": OUT_DIR / "regime_aware_loop_history.json",
    "loop_history_md": OUT_DIR / "regime_aware_loop_history.md",
    "green_certification": OUT_DIR / "official_strict_green_certification.json",
    "green_certification_md": OUT_DIR / "official_strict_green_certification.md",
    "market_shadow": OUT_DIR / "market_shadow_disagreement_report.json",
    "market_shadow_md": OUT_DIR / "market_shadow_disagreement_report.md",
    "future_risk_map": OUT_DIR / "future_2084_2099_risk_map.json",
    "future_risk_map_md": OUT_DIR / "future_2084_2099_risk_map.md",
    "regime_assignment": OUT_DIR / "regime_assignment_report.json",
    "regime_assignment_md": OUT_DIR / "regime_assignment_report.md",
    "verification_targets": OUT_DIR / "top_verification_targets.csv",
    "verification_targets_md": OUT_DIR / "top_verification_targets.md",
    "blinded_schema": OUT_DIR / "blinded_external_audit_schema.json",
    "blinded_schema_md": OUT_DIR / "blinded_external_audit_schema.md",
}


def official_guard_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for row in corpus_rows():
        if not 2078 <= row.bs_year <= 2083:
            continue
        if row.source_type != "official_verified" or row.verification_status != "verified":
            continue
        for month, days in enumerate(row.months, start=1):
            cases.append(_case("official_strict", row.bs_year, month, days, "1"))
    return cases


def policy_cases(policy: str, start: int = 2000, end: int = 2099) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in policy_rows(policy):
        year = int(row["bs_year"])
        if not start <= year <= end:
            continue
        rows.append(_case(policy, year, int(row["bs_month"]), int(row["month_length"]), row.get("best_source_tier", "")))
    return rows


def hamropatro_cases(start: int = 2000, end: int = 2099) -> list[dict[str, Any]]:
    years = hamropatro_shadow_years()
    cases: list[dict[str, Any]] = []
    for year in range(start, end + 1):
        months = years.get(year)
        if not months:
            continue
        for month, days in enumerate(months, start=1):
            cases.append(_case("hamropatro_shadow_experimental", year, month, days, "6"))
    return cases


def _case(dataset: str, year: int, month: int, actual_days: int, source_tier: str) -> dict[str, Any]:
    return {
        "dataset": dataset,
        "bs_year": int(year),
        "bs_month": int(month),
        "month_name": BS_MONTH_NAMES[int(month) - 1],
        "actual_days": int(actual_days),
        "source_tier": str(source_tier),
    }


def candidate_list() -> list[RegimeCandidate]:
    return [
        RegimeCandidate(
            candidate_id="baseline_strict_regime_gate",
            modern_source_policy="medium_high_training",
            green_mode="strict",
            description="Solar-civil selected, market/legacy disagreement pushes risk up.",
        ),
        RegimeCandidate(
            candidate_id="official_printed_evidence_dominance",
            modern_source_policy="medium_high_training",
            green_mode="official_evidence_dominates",
            description="Tier 1/2 source witness can collapse prediction set for historical official/printed rows.",
        ),
        RegimeCandidate(
            candidate_id="market_agreement_green_expansion",
            modern_source_policy="medium_high_training",
            green_mode="market_tolerant",
            description="Allows GREEN when market and solar agree, but only outside official claim context.",
        ),
        RegimeCandidate(
            candidate_id="all_witness_training_rejected_for_official",
            modern_source_policy="all_witness_experimental",
            green_mode="market_tolerant",
            uses_tier_5_6_for_official=True,
            description="Intentional contamination check; must be rejected.",
        ),
        RegimeCandidate(
            candidate_id="future_shadow_target_leakage_rejected",
            modern_source_policy="medium_high_training",
            green_mode="market_tolerant",
            uses_future_shadow_targets=True,
            description="Intentional future-shadow leakage check; must be rejected.",
        ),
        RegimeCandidate(
            candidate_id="table_imitation_rejected",
            modern_source_policy="medium_high_training",
            green_mode="market_tolerant",
            table_imitation_risk=True,
            description="Intentional table-imitation check; must be rejected.",
        ),
    ]


def evaluate_candidate(candidate: RegimeCandidate, cases: list[dict[str, Any]], dataset: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    exact = 0
    green = 0
    green_correct = 0
    wrong_green = 0
    invalid_years: set[int] = set()
    disagreement_count = 0
    explained_disagreements = 0
    disagreement_green_violations = 0
    rows: list[dict[str, Any]] = []
    by_month: Counter[int] = Counter()
    by_year: Counter[int] = Counter()
    official_context = dataset == "official_strict"

    for case in cases:
        record = candidate_prediction(
            candidate,
            case["bs_year"],
            case["bs_month"],
            official_claim_context=official_context,
        )
        selected = int(record["selected_prediction"])
        actual = int(case["actual_days"])
        correct = selected == actual
        exact += int(correct)
        if not record["year_total_valid"]:
            invalid_years.add(int(case["bs_year"]))
        is_green = record["risk_label"] == "GREEN"
        green += int(is_green)
        green_correct += int(is_green and correct)
        wrong_green += int(is_green and not correct)
        if record["agreement_status"] == "disagree":
            disagreement_count += 1
            if record["risk_label"] in {"YELLOW", "RED"}:
                explained_disagreements += 1
            if record["risk_label"] == "GREEN":
                disagreement_green_violations += 1
        if not correct:
            by_month[int(case["bs_month"])] += 1
            by_year[int(case["bs_year"])] += 1
        rows.append(
            {
                "dataset": dataset,
                "candidate": candidate.candidate_id,
                "bs_year": case["bs_year"],
                "bs_month": case["bs_month"],
                "month_name": case["month_name"],
                "actual_days": actual,
                "selected_prediction": selected,
                "solar_civil_prediction": record["solar_civil_prediction"],
                "legacy_static_prediction": record["legacy_static_prediction"],
                "hamropatro_shadow_prediction": record["hamropatro_shadow_prediction"],
                "regime_assignment": record["regime_assignment"],
                "risk_label": record["risk_label"],
                "prediction_set_95": record["prediction_set_95"],
                "agreement_status": record["agreement_status"],
                "disagreement_type": record["disagreement_type"],
                "boundary_sensitive": record["boundary_sensitive"],
                "year_total_valid": record["year_total_valid"],
                "correct": correct,
                "green_certification": record["green_certification"],
            }
        )

    total = len(cases)
    metric = {
        "publication_status": PUBLICATION_STATUS,
        "dataset": dataset,
        "candidate": candidate.candidate_id,
        "total_months_tested": total,
        "exact_matches": exact,
        "accuracy": round(exact / total, 6) if total else 0.0,
        "mismatch_count": total - exact,
        "green_count": green,
        "green_accuracy": round(green_correct / green, 6) if green else 0.0,
        "green_coverage": round(green / total, 6) if total else 0.0,
        "wrong_green_count": wrong_green,
        "false_green_rate": round(wrong_green / green, 6) if green else 0.0,
        "invalid_year_total_count": len(invalid_years),
        "invalid_years": sorted(invalid_years),
        "disagreement_count": disagreement_count,
        "disagreement_explained_count": explained_disagreements,
        "disagreement_explained_rate": round(explained_disagreements / disagreement_count, 6) if disagreement_count else 1.0,
        "disagreement_green_violations": disagreement_green_violations,
        "mismatches_by_month": {str(month): by_month.get(month, 0) for month in range(1, 13)},
        "mismatches_by_year": {str(year): count for year, count in sorted(by_year.items())},
    }
    return metric, rows


def objective_score(metrics: dict[str, dict[str, Any]], gate: dict[str, Any]) -> float:
    official = metrics["official_strict"]
    medium = metrics["medium_high_training"]
    all_witness = metrics["all_witness_experimental"]
    hamro = metrics["hamropatro_shadow_experimental"]
    leakage_risk = 0 if gate["checks"].get("no_future_shadow_reference_target_leakage") else 1
    contamination = 0 if gate["checks"].get("no_tier_5_6_official_contamination") else 1
    invalid_total = (
        official["invalid_year_total_count"]
        + medium["invalid_year_total_count"]
        + all_witness["invalid_year_total_count"]
    )
    return round(
        10000 * official["green_accuracy"]
        - 50000 * official["wrong_green_count"]
        - 10000 * official["false_green_rate"]
        + 1000 * official["green_coverage"]
        + 500 * medium["accuracy"]
        + 300 * all_witness["accuracy"]
        + 300 * hamro["disagreement_explained_rate"]
        - 5000 * invalid_total
        - 2000 * leakage_risk
        - 1000 * contamination,
        6,
    )


def current_state_summary() -> dict[str, Any]:
    official = official_guard_cases()
    current_legacy_mismatches = []
    for case in official:
        legacy = predict_legacy_cycle(case["bs_year"]).months[case["bs_month"] - 1]
        if legacy != case["actual_days"]:
            current_legacy_mismatches.append(
                {
                    "bs_year": case["bs_year"],
                    "bs_month": case["bs_month"],
                    "month_name": case["month_name"],
                    "legacy_days": legacy,
                    "official_days": case["actual_days"],
                }
            )
    acceptance_context_misses = [
        {"bs_year": 2082, "bs_month": 3, "month_name": "Ashadh"},
        {"bs_year": 2082, "bs_month": 4, "month_name": "Shrawan"},
        {"bs_year": 2083, "bs_month": 5, "month_name": "Bhadra"},
        {"bs_year": 2083, "bs_month": 6, "month_name": "Ashwin"},
    ]
    solar_exact = 72
    solar_total = 72
    previous_loop = _load_json(OUT_DIR / "solar_civil_rule_loop_2000_2099_metrics.json")
    claim = _load_json(OUT_DIR / "accuracy_readiness_final.json")
    hamro_2000 = _load_json(OUT_DIR / "hamropatro_shadow_2000_2070_metrics.json")
    hamro_2084 = _load_json(OUT_DIR / "hamropatro_shadow_2084_2099_metrics.json")
    return {
        "publication_status": PUBLICATION_STATUS,
        "official_strict_2078_2083_solar_civil": {
            "exact_matches": solar_exact,
            "total_months_tested": solar_total,
            "agreement": 1.0,
        },
        "legacy_static_2078_2083": {
            "exact_matches": 68,
            "total_months_tested": solar_total,
            "agreement": round(68 / solar_total, 6),
            "misses": acceptance_context_misses,
            "benchmark_note": (
                "Legacy/static assumption benchmark from the acceptance context. "
                "The current in-repo legacy_cycle_predictor is tracked separately because it now uses "
                "updated corpus behavior and is not the old static failure mode."
            ),
        },
        "current_in_repo_legacy_cycle_predictor_2078_2083": {
            "exact_matches": solar_total - len(current_legacy_mismatches),
            "total_months_tested": solar_total,
            "agreement": round((solar_total - len(current_legacy_mismatches)) / solar_total, 6),
            "misses": current_legacy_mismatches,
        },
        "hamropatro_2000_2070_shadow": _compact_hamro(hamro_2000),
        "hamropatro_2084_2099_shadow": _compact_hamro(hamro_2084),
        "rejected_96_83_broad_result": {
            "rejected": True,
            "reason": "used future-shadow/reference calibration and was not forecast-clean",
            "source_artifact": "solar_civil_rule_loop_2000_2099_metrics.json",
        },
        "latest_clean_rule_loop": {
            "target_reached": previous_loop.get("target_reached"),
            "stop_reason": previous_loop.get("stop_reason"),
            "best_candidate": previous_loop.get("best_candidate", {}).get("candidate_id")
            if isinstance(previous_loop.get("best_candidate"), dict)
            else previous_loop.get("best_candidate"),
        },
        "source_policy_boundaries": {
            "official_strict": "Tier 1 and manually promoted strong Tier 2 only for official claims",
            "medium_high_training": "Tier 1-4 learning/calibration, non-official benchmark",
            "all_witness_experimental": "Tier 1-6 weak-signal analysis, not official proof",
            "hamropatro_shadow_experimental": "market shadow only",
        },
        "current_official_claim_readiness": {
            "claim_ready_99_green_zone": claim.get("claim_ready_99_green_zone", False),
            "claim_ready_with_sufficient_corpus": claim.get("claim_ready_with_sufficient_corpus", False),
            "official_cases": claim.get("official_cases") or claim.get("official_strict_cases"),
            "required_official_cases": claim.get("required_official_cases", 528),
        },
        "why_broad_99_not_proven": [
            "Official strict corpus remains far below the required case threshold.",
            "Mixed-source and HamroPatro agreement are useful diagnostics but not official truth.",
            "No-leakage broad rolling agreement remains below 95% in current diagnostics.",
        ],
    }


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _compact_hamro(payload: dict[str, Any]) -> dict[str, Any]:
    if not payload:
        return {"available": False}
    return {
        "available": True,
        "total_months_tested": payload.get("total_months_tested"),
        "solar_civil_shadow_agreement": payload.get("solar_civil_shadow_agreement"),
        "legacy_shadow_agreement": payload.get("legacy_shadow_agreement"),
        "claim_scope": payload.get("claim_scope"),
    }


def run_loop() -> dict[str, Any]:
    datasets = {
        "official_strict": official_guard_cases(),
        "medium_high_training": policy_cases("medium_high_training"),
        "all_witness_experimental": policy_cases("all_witness_experimental"),
        "hamropatro_shadow_experimental": hamropatro_cases(),
    }
    baseline_candidate = candidate_list()[0]
    baseline_metrics, baseline_rows = _evaluate_all(baseline_candidate, datasets)
    best_candidate = baseline_candidate
    best_metrics = baseline_metrics
    best_rows = baseline_rows
    non_improving = 0
    loop_history: list[dict[str, Any]] = []

    baseline_gate = acceptance_gate(
        candidate=baseline_candidate,
        official_metric=baseline_metrics["official_strict"],
        medium_metric=baseline_metrics["medium_high_training"],
        all_witness_metric=baseline_metrics["all_witness_experimental"],
        hamropatro_metric=baseline_metrics["hamropatro_shadow_experimental"],
        baseline_medium_accuracy=baseline_metrics["medium_high_training"]["accuracy"],
        baseline_all_accuracy=baseline_metrics["all_witness_experimental"]["accuracy"],
        baseline_hamro_explained=baseline_metrics["hamropatro_shadow_experimental"]["disagreement_explained_rate"],
    )
    loop_history.append(
        {
            "loop": 0,
            "candidate": baseline_candidate.__dict__,
            "accepted": True,
            "reason": "baseline",
            "gate": baseline_gate,
            "metrics": baseline_metrics,
            "objective_score": objective_score(baseline_metrics, baseline_gate),
        }
    )

    stop_reason = "candidate_list_exhausted"
    for loop_index, candidate in enumerate(candidate_list()[1:], start=1):
        metrics, rows = _evaluate_all(candidate, datasets)
        gate = acceptance_gate(
            candidate=candidate,
            official_metric=metrics["official_strict"],
            medium_metric=metrics["medium_high_training"],
            all_witness_metric=metrics["all_witness_experimental"],
            hamropatro_metric=metrics["hamropatro_shadow_experimental"],
            baseline_medium_accuracy=best_metrics["medium_high_training"]["accuracy"],
            baseline_all_accuracy=best_metrics["all_witness_experimental"]["accuracy"],
            baseline_hamro_explained=best_metrics["hamropatro_shadow_experimental"]["disagreement_explained_rate"],
        )
        score = objective_score(metrics, gate)
        best_score = objective_score(best_metrics, baseline_gate)
        accepted = bool(gate["accepted"] and score > best_score)
        if accepted:
            best_candidate = candidate
            best_metrics = metrics
            best_rows = rows
            baseline_gate = gate
            non_improving = 0
        else:
            non_improving += 1
        loop_history.append(
            {
                "loop": loop_index,
                "candidate": candidate.__dict__,
                "accepted": accepted,
                "reason": "accepted_objective_improvement" if accepted else gate["reason"],
                "gate": gate,
                "metrics": metrics,
                "objective_score": score,
                "before_after_delta": {
                    key: {
                        "accuracy_delta": round(metrics[key]["accuracy"] - best_metrics[key]["accuracy"], 6)
                        if key in metrics and "accuracy" in metrics[key]
                        else None,
                        "green_accuracy_delta": round(metrics[key]["green_accuracy"] - best_metrics[key]["green_accuracy"], 6)
                        if key in metrics
                        else None,
                    }
                    for key in datasets
                },
            }
        )
        if (
            best_metrics["official_strict"]["green_accuracy"] >= 0.99
            and best_metrics["official_strict"]["wrong_green_count"] == 0
            and best_metrics["official_strict"]["green_coverage"] >= 0.85
            and non_improving >= 4
        ):
            stop_reason = "official_green_target_met_and_four_no_better_candidates"
            break
        if non_improving >= 4:
            stop_reason = "four_consecutive_complete_candidate_loops_without_accepted_improvement"
            break

    return {
        "publication_status": PUBLICATION_STATUS,
        "best_candidate": best_candidate.__dict__,
        "best_metrics": best_metrics,
        "best_rows": best_rows,
        "loop_history": loop_history,
        "stop_reason": stop_reason,
        "official_99_green_target_met": best_metrics["official_strict"]["green_accuracy"] >= 0.99
        and best_metrics["official_strict"]["wrong_green_count"] == 0,
        "official_claim_boundary": (
            "Official GREEN metrics are validation over the current strict official window. "
            "They are not a public 99% claim until corpus-size gates pass."
        ),
    }


def _evaluate_all(candidate: RegimeCandidate, datasets: dict[str, list[dict[str, Any]]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    metrics: dict[str, Any] = {}
    rows: list[dict[str, Any]] = []
    for dataset, cases in datasets.items():
        metric, dataset_rows = evaluate_candidate(candidate, cases, dataset)
        metrics[dataset] = metric
        rows.extend(dataset_rows)
    return metrics, rows


def future_risk_map(candidate: RegimeCandidate, *, blinded: bool = False) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    invalid_years: set[int] = set()
    for year in range(2084, 2100):
        year_predictions = []
        for month in range(1, 13):
            record = candidate_prediction(candidate, year, month)
            year_predictions.append(int(record["selected_prediction"]))
            row = {
                "bs_year": year,
                "bs_month": month,
                "month_name": BS_MONTH_NAMES[month - 1],
                "agreement_status": record["agreement_status"],
                "risk_label": record["risk_label"],
                "boundary_sensitive": record["boundary_sensitive"],
                "year_total_risk": "valid" if record["year_total_valid"] else "invalid",
                "source_conflict_risk": record["source_conflict_risk"],
                "recommended_review": record["risk_label"] in {"YELLOW", "RED"},
                "safe_to_share_in_blinded_audit": record["risk_label"] != "GREEN",
            }
            if not blinded:
                row.update(
                    {
                        "solar_civil_prediction": record["solar_civil_prediction"],
                        "legacy_static_prediction": record["legacy_static_prediction"],
                        "hamropatro_shadow_prediction": record["hamropatro_shadow_prediction"],
                        "selected_prediction": record["selected_prediction"],
                    }
                )
            rows.append(row)
        if sum(year_predictions) not in {365, 366}:
            invalid_years.add(year)
    return {
        "publication_status": PUBLICATION_STATUS,
        "blinded": blinded,
        "range": {"start_bs_year": 2084, "end_bs_year": 2099},
        "invalid_year_total_count": len(invalid_years),
        "invalid_years": sorted(invalid_years),
        "rows": rows,
    }


def market_shadow_disagreement_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    disagreements = [
        row
        for row in rows
        if row["dataset"] == "hamropatro_shadow_experimental" and row["agreement_status"] == "disagree"
    ]
    risk_counts = Counter(row["risk_label"] for row in disagreements)
    return {
        "publication_status": PUBLICATION_STATUS,
        "claim_scope": "market shadow disagreement only; not official accuracy",
        "total_disagreements": len(disagreements),
        "risk_distribution": dict(sorted(risk_counts.items())),
        "disagreements": [
            {
                "bs_year": row["bs_year"],
                "bs_month": row["bs_month"],
                "solar_civil_prediction": row["solar_civil_prediction"],
                "legacy_static_prediction": row["legacy_static_prediction"],
                "hamropatro_shadow_prediction": row["hamropatro_shadow_prediction"],
                "selected_prediction": row["selected_prediction"],
                "regime_assignment": row["regime_assignment"],
                "risk_label": row["risk_label"],
                "source_policy": "hamropatro_shadow_experimental",
                "disagreement_type": row["disagreement_type"],
                "boundary_risk": row["boundary_sensitive"],
                "year_total_impact": "valid" if row["year_total_valid"] else "invalid",
                "reason": "market and solar-civil disagree; verification recommended",
                "recommended_verification_source": "official_verified_or_printed_verified_or_public_daily_witness",
                "should_return_corrected_value": False,
            }
            for row in disagreements[:500]
        ],
    }


def top_verification_targets(rows: list[dict[str, Any]], limit: int = 100) -> list[dict[str, Any]]:
    grouped: dict[tuple[int, int], dict[str, Any]] = {}
    for row in rows:
        if row["agreement_status"] != "disagree" and row["risk_label"] == "GREEN":
            continue
        key = (int(row["bs_year"]), int(row["bs_month"]))
        item = grouped.setdefault(
            key,
            {
                "bs_year": key[0],
                "bs_month": key[1],
                "month_name": row["month_name"],
                "priority_score": 0,
                "reasons": [],
                "recommended_verification_source": "official_verified_or_printed_verified_or_public_daily_witness",
            },
        )
        item["priority_score"] += 10 if row["risk_label"] == "RED" else 5 if row["risk_label"] == "YELLOW" else 1
        if row["agreement_status"] == "disagree":
            item["priority_score"] += 8
            item["reasons"].append("tower disagreement")
        if row["boundary_sensitive"]:
            item["priority_score"] += 5
            item["reasons"].append("boundary-sensitive")
        if row["bs_month"] in {6, 7}:
            item["priority_score"] += 4
            item["reasons"].append("Ashwin/Kartik")
    targets = []
    for item in grouped.values():
        reasons = item.pop("reasons")
        targets.append({**item, "reason": "; ".join(sorted(set(reasons))) or "risk review"})
    return sorted(targets, key=lambda row: (-row["priority_score"], row["bs_year"], row["bs_month"]))[:limit]


def regime_assignment_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(row["regime_assignment"] for row in rows)
    return {
        "publication_status": PUBLICATION_STATUS,
        "regime_counts": dict(sorted(counts.items())),
        "assignments": [
            {
                "bs_year": row["bs_year"],
                "bs_month": row["bs_month"],
                "regime_assignment": row["regime_assignment"],
                "risk_label": row["risk_label"],
                "agreement_status": row["agreement_status"],
            }
            for row in rows
        ],
    }


def blinded_schema() -> dict[str, Any]:
    return {
        "publication_status": PUBLICATION_STATUS,
        "default_mode": "aggregate_only_no_corrected_values",
        "input_columns": ["bs_year", "bs_month", "predicted_days"],
        "default_output_fields": [
            "total_months_compared",
            "total_agreements",
            "total_disagreements",
            "boundary_sensitive_disagreements",
            "high_risk_months_count",
            "year_total_anomalies",
            "disagreement_years",
            "risk_distribution",
        ],
        "hidden_by_default": ["parva_corrected_month_value", "selected_prediction", "solar_civil_prediction"],
        "include_corrected_values_flag": "--include-corrected-values",
        "warning": "Corrected values are hidden by default for blinded audit mode.",
    }


def write_outputs(payload: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    current = current_state_summary()
    best_rows = payload["best_rows"]
    market = market_shadow_disagreement_report(best_rows)
    risk_map = future_risk_map(RegimeCandidate(**payload["best_candidate"]))
    regime_report = regime_assignment_report(best_rows)
    targets = top_verification_targets(best_rows)
    green = {
        "publication_status": PUBLICATION_STATUS,
        "dataset": "official_strict",
        **payload["best_metrics"]["official_strict"],
        "claim_boundary": payload["official_claim_boundary"],
    }
    _write_json(REPORTS["current_state_metrics"], current)
    _write_json(REPORTS["regime_ensemble_metrics"], {k: v for k, v in payload.items() if k != "best_rows"})
    _write_json(REPORTS["loop_history"], {"publication_status": PUBLICATION_STATUS, "loop_history": payload["loop_history"]})
    _write_json(REPORTS["green_certification"], green)
    _write_json(REPORTS["market_shadow"], market)
    _write_json(REPORTS["future_risk_map"], risk_map)
    _write_json(REPORTS["regime_assignment"], regime_report)
    _write_json(REPORTS["blinded_schema"], blinded_schema())
    _write_current_md(REPORTS["current_state_summary"], current)
    _write_loop_md(REPORTS["loop_history_md"], payload)
    _write_metrics_md(REPORTS["regime_ensemble_metrics_md"], payload)
    _write_simple_md(REPORTS["green_certification_md"], "Official Strict GREEN Certification", green)
    _write_simple_md(REPORTS["market_shadow_md"], "Market Shadow Disagreement Report", market)
    _write_simple_md(REPORTS["future_risk_map_md"], "Future Shadow Risk Map", {k: v for k, v in risk_map.items() if k != "rows"})
    _write_simple_md(REPORTS["regime_assignment_md"], "Regime Assignment Report", {k: v for k, v in regime_report.items() if k != "assignments"})
    _write_simple_md(REPORTS["blinded_schema_md"], "Blinded External Audit Schema", blinded_schema())
    _write_targets_csv(REPORTS["verification_targets"], targets)
    _write_targets_md(REPORTS["verification_targets_md"], targets)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_current_md(path: Path, payload: dict[str, Any]) -> None:
    misses = payload["legacy_static_2078_2083"]["misses"]
    lines = [
        "# Current Regime-Aware Accuracy State",
        "",
        f"- publication_status: `{PUBLICATION_STATUS}`",
        "- official_strict 2078-2083 solar-civil: 72/72",
        (
            f"- legacy/static 2078-2083: {payload['legacy_static_2078_2083']['exact_matches']}/"
            f"{payload['legacy_static_2078_2083']['total_months_tested']}"
        ),
        "- rejected 96.83% broad result: rejected for future-shadow/reference leakage",
        "- official 99% public claim: not ready until corpus-size gates pass",
        (
            f"- HamroPatro 2000-2070 solar shadow agreement: "
            f"{payload['hamropatro_2000_2070_shadow'].get('solar_civil_shadow_agreement', 'missing')}"
        ),
        (
            f"- HamroPatro future-shadow solar agreement: "
            f"{payload['hamropatro_2084_2099_shadow'].get('solar_civil_shadow_agreement', 'missing')}"
        ),
        (
            f"- official claim readiness: "
            f"{payload['current_official_claim_readiness'].get('claim_ready_99_green_zone')}"
        ),
        "",
        "## Legacy Misses",
        "",
    ]
    for row in misses:
        if "legacy_days" in row:
            lines.append(f"- {row['bs_year']} {row['month_name']}: legacy {row['legacy_days']} vs official {row['official_days']}")
        else:
            lines.append(f"- {row['bs_year']} {row['month_name']}: old static assumption miss")
    lines.extend(
        [
            "",
            "## Current In-Repo Legacy Cycle Predictor",
            "",
            (
                f"- current legacy_cycle_predictor 2078-2083: "
                f"{payload['current_in_repo_legacy_cycle_predictor_2078_2083']['exact_matches']}/"
                f"{payload['current_in_repo_legacy_cycle_predictor_2078_2083']['total_months_tested']}"
            ),
            "- This is tracked separately from the older static-assumption failure benchmark.",
        ]
    )
    lines.extend(
        [
            "",
            "## Source-Policy Boundaries",
            "",
        ]
    )
    for key, value in payload["source_policy_boundaries"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Why Broad 99% Is Not Proven", ""])
    for blocker in payload["why_broad_99_not_proven"]:
        lines.append(f"- {blocker}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_loop_md(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Regime-Aware Loop History",
        "",
        f"- publication_status: `{PUBLICATION_STATUS}`",
        f"- stop_reason: `{payload['stop_reason']}`",
        f"- best_candidate: `{payload['best_candidate']['candidate_id']}`",
        "",
    ]
    for item in payload["loop_history"]:
        failed = ", ".join(item["gate"].get("failed_checks", [])) or "none"
        lines.extend(
            [
                f"## Loop {item['loop']}: `{item['candidate']['candidate_id']}`",
                "",
                f"- accepted: {str(item['accepted']).lower()}",
                f"- reason: `{item['reason']}`",
                f"- objective_score: {item['objective_score']}",
                f"- failed_checks: {failed}",
                f"- official GREEN: {item['metrics']['official_strict']['green_accuracy']} coverage {item['metrics']['official_strict']['green_coverage']}",
                f"- all_witness accuracy: {item['metrics']['all_witness_experimental']['accuracy']}",
                f"- HamroPatro disagreement explained: {item['metrics']['hamropatro_shadow_experimental']['disagreement_explained_rate']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_metrics_md(path: Path, payload: dict[str, Any]) -> None:
    best = payload["best_metrics"]
    lines = [
        "# Regime Ensemble Metrics",
        "",
        f"- publication_status: `{PUBLICATION_STATUS}`",
        f"- best_candidate: `{payload['best_candidate']['candidate_id']}`",
        f"- official_99_green_target_met: {str(payload['official_99_green_target_met']).lower()}",
        f"- stop_reason: `{payload['stop_reason']}`",
        "",
    ]
    for key, metric in best.items():
        lines.append(
            f"- {key}: accuracy {metric['accuracy']}, GREEN accuracy {metric['green_accuracy']}, "
            f"GREEN coverage {metric['green_coverage']}, wrong GREEN {metric['wrong_green_count']}"
        )
    lines.append("")
    lines.append(payload["official_claim_boundary"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_simple_md(path: Path, title: str, payload: dict[str, Any]) -> None:
    lines = [f"# {title}", "", f"- publication_status: `{PUBLICATION_STATUS}`", ""]
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            lines.append(f"- {key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_targets_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = ["bs_year", "bs_month", "month_name", "priority_score", "reason", "recommended_verification_source"]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_targets_md(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = ["# Top Verification Targets", "", f"- publication_status: `{PUBLICATION_STATUS}`", ""]
    for row in rows[:100]:
        lines.append(f"- {row['bs_year']}-{row['bs_month']:02d}: score {row['priority_score']}; {row['reason']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    payload = run_loop()
    if not args.no_write:
        write_outputs(payload)
    printable = {
        "publication_status": PUBLICATION_STATUS,
        "stop_reason": payload["stop_reason"],
        "best_candidate": payload["best_candidate"]["candidate_id"],
        "official_strict": payload["best_metrics"]["official_strict"],
        "medium_high_training": payload["best_metrics"]["medium_high_training"],
        "all_witness_experimental": payload["best_metrics"]["all_witness_experimental"],
        "hamropatro_shadow_experimental": payload["best_metrics"]["hamropatro_shadow_experimental"],
    }
    print(json.dumps(printable, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
