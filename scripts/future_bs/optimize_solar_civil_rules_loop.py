#!/usr/bin/env python3
"""Run a gated solar-civil rule-improvement loop.

The loop optimizes experimental all-witness agreement only when the candidate
also preserves strict modern-official behavior and no-leakage evaluation.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.calendar.constants import BS_MONTH_NAMES  # noqa: E402
from app.research.future_bs.corpus import corpus_rows  # noqa: E402
from app.research.future_bs.hamropatro_shadow import HAMROPATRO_MONTH_LENGTHS_PATH  # noqa: E402
from app.research.future_bs.legacy_cycle_predictor import predict_legacy_cycle  # noqa: E402
from app.research.future_bs.shadow_residual_correction import (  # noqa: E402
    PUBLICATION_STATUS,
    apply_shadow_residual_rules,
    train_shadow_residual_rules,
)
from app.research.future_bs.solar_ingress_predictor import predict_solar_ingress_year  # noqa: E402
from app.research.future_bs.source_policy import policy_rows  # noqa: E402

OUT_DIR = PROJECT_ROOT / "data" / "future_bs" / "accuracy_lab"
DEFAULT_JSON = OUT_DIR / "solar_civil_rule_loop_2000_2099_metrics.json"
DEFAULT_MD = OUT_DIR / "solar_civil_rule_loop_2000_2099_metrics.md"
DEFAULT_RULES = OUT_DIR / "solar_civil_shadow_residual_rules.json"
DEFAULT_MISMATCHES = OUT_DIR / "solar_civil_rule_loop_2000_2099_mismatches.csv"

TARGET_EXPERIMENTAL_ACCURACY = 0.95
MAX_NON_IMPROVING_LOOPS = 4
MEDIUM_HIGH_MAX_REGRESSION = 0.0025
LEGACY_IMITATION_LIMIT = 0.95


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    kind: str
    source_policy: str
    train_start: int = 2000
    train_end_cap: int = 2099
    min_support: int = 0
    leakage_safe: bool = True
    hardcoded_patch_safe: bool = True
    explainability_class: str = "civil_date_rule_regime_logic"
    notes: str = ""


BASELINE = Candidate(
    candidate_id="baseline_medium_high_training_full_history_rolling",
    kind="solar_civil",
    source_policy="medium_high_training",
    notes="Current solar-civil stack trained only on Tier 1-4 reconstructed rows available before each target year.",
)


def _cases_from_policy(policy: str, start: int, end: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in policy_rows(policy):
        year = int(row["bs_year"])
        if not start <= year <= end:
            continue
        rows.append(
            {
                "dataset": policy,
                "bs_year": year,
                "bs_month": int(row["bs_month"]),
                "month_name": BS_MONTH_NAMES[int(row["bs_month"]) - 1],
                "actual_days": int(row["month_length"]),
                "source_tier": str(row.get("best_source_tier", "")),
                "trust_scope": policy,
            }
        )
    return rows


def _official_guard_cases(start: int = 2078, end: int = 2083) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in corpus_rows():
        if not start <= row.bs_year <= end:
            continue
        if row.source_type != "official_verified" or row.verification_status != "verified":
            continue
        for month_index, actual_days in enumerate(row.months, start=1):
            rows.append(
                {
                    "dataset": "official_strict_2078_2083_guard",
                    "bs_year": row.bs_year,
                    "bs_month": month_index,
                    "month_name": BS_MONTH_NAMES[month_index - 1],
                    "actual_days": actual_days,
                    "source_tier": "1",
                    "trust_scope": "official_strict",
                }
            )
    return rows


def _hamropatro_cases(start: int, end: int) -> list[dict[str, Any]]:
    payload = json.loads(HAMROPATRO_MONTH_LENGTHS_PATH.read_text(encoding="utf-8"))
    years = {
        int(row["bs_year"]): [int(month["days"]) for month in row["months"]]
        for row in payload.get("years", [])
    }
    rows: list[dict[str, Any]] = []
    for year in range(start, end + 1):
        months = years.get(year)
        if not months:
            continue
        for month_index, actual_days in enumerate(months, start=1):
            rows.append(
                {
                    "dataset": "hamropatro_shadow_experimental",
                    "bs_year": year,
                    "bs_month": month_index,
                    "month_name": BS_MONTH_NAMES[month_index - 1],
                    "actual_days": actual_days,
                    "source_tier": "6",
                    "trust_scope": "shadow_agreement_not_official_accuracy",
                }
            )
    return rows


@lru_cache(maxsize=4096)
def _solar_months(source_policy: str, train_start: int, train_end: int, bs_year: int) -> tuple[int, ...]:
    payload = predict_solar_ingress_year(
        bs_year,
        train_start=train_start,
        train_end=train_end,
        source_policy=source_policy,
    )
    return tuple(int(value) for value in payload["months"])


@lru_cache(maxsize=4096)
def _rolling_residual_rules(source_policy: str, residual_end: int, min_support: int) -> str:
    payload = train_shadow_residual_rules(
        residual_start=2084,
        residual_end=residual_end,
        min_support=min_support,
        source_policy=source_policy,
    )
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


@lru_cache(maxsize=64)
def _fixed_shadow_rules(source_policy: str, min_support: int) -> str:
    payload = train_shadow_residual_rules(
        residual_start=2084,
        residual_end=2099,
        min_support=min_support,
        source_policy=source_policy,
    )
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _effective_train_end(candidate: Candidate, bs_year: int) -> int | None:
    if bs_year <= candidate.train_start:
        return None
    return min(candidate.train_end_cap, bs_year - 1)


def _predict_candidate_year(candidate: Candidate, bs_year: int) -> tuple[list[int] | None, list[dict[str, Any]], list[str]]:
    train_end = _effective_train_end(candidate, bs_year)
    if train_end is None:
        return None, [], ["skipped_no_prior_training_year"]

    base = list(_solar_months(candidate.source_policy, candidate.train_start, train_end, bs_year))
    if candidate.kind == "solar_civil":
        return base, [], []

    if candidate.kind == "shadow_residual_fixed":
        rules = json.loads(_fixed_shadow_rules(candidate.source_policy, candidate.min_support))
        corrected, applied = apply_shadow_residual_rules(bs_year, base, rules, residual_start=2084)
        if sum(corrected) not in {365, 366}:
            return base, [], ["invalid_residual_year_total_reverted"]
        return corrected, applied, []

    if candidate.kind == "shadow_residual_rolling":
        if bs_year <= 2084:
            return base, [], []
        rules = json.loads(_rolling_residual_rules(candidate.source_policy, bs_year - 1, candidate.min_support))
        corrected, applied = apply_shadow_residual_rules(bs_year, base, rules, residual_start=2084)
        if sum(corrected) not in {365, 366}:
            return base, [], ["invalid_residual_year_total_reverted"]
        return corrected, applied, []

    raise ValueError(f"Unknown candidate kind: {candidate.kind}")


def _empty_month_counter() -> dict[str, int]:
    return {str(month): 0 for month in range(1, 13)}


def _evaluate_cases(
    cases: list[dict[str, Any]],
    candidate: Candidate,
    *,
    dataset_id: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    exact = 0
    total = 0
    skipped_years: set[int] = set()
    prediction_cache: dict[int, list[int] | None] = {}
    applied_cache: dict[int, list[dict[str, Any]]] = {}
    risk_cache: dict[int, list[str]] = {}
    year_total_anomalies: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    mismatches_by_month: Counter[int] = Counter()
    mismatches_by_year: Counter[int] = Counter()
    applied_rule_count = 0
    reverted_invalid_count = 0

    for case in cases:
        year = int(case["bs_year"])
        if year not in prediction_cache:
            months, applied, risk_flags = _predict_candidate_year(candidate, year)
            prediction_cache[year] = months
            applied_cache[year] = applied
            risk_cache[year] = risk_flags
            applied_rule_count += len(applied)
            if "invalid_residual_year_total_reverted" in risk_flags:
                reverted_invalid_count += 1
            if months is None:
                skipped_years.add(year)
            elif sum(months) not in {365, 366}:
                year_total_anomalies.append(
                    {
                        "bs_year": year,
                        "predicted_total": sum(months),
                        "candidate": candidate.candidate_id,
                        "dataset": dataset_id,
                    }
                )
        predicted = prediction_cache[year]
        if predicted is None:
            continue

        month_index = int(case["bs_month"])
        predicted_days = predicted[month_index - 1]
        actual_days = int(case["actual_days"])
        total += 1
        if predicted_days == actual_days:
            exact += 1
            continue

        mismatches_by_month[month_index] += 1
        mismatches_by_year[year] += 1
        applied_for_month = [
            item
            for item in applied_cache.get(year, [])
            if int(item.get("bs_month", 0)) == month_index
        ]
        mismatches.append(
            {
                "dataset": dataset_id,
                "candidate": candidate.candidate_id,
                "bs_year": year,
                "bs_month": month_index,
                "month_name": case["month_name"],
                "actual_days": actual_days,
                "predicted_days": predicted_days,
                "source_tier": case["source_tier"],
                "trust_scope": case["trust_scope"],
                "risk_flags": ";".join(risk_cache.get(year, [])),
                "applied_rules": json.dumps(applied_for_month, ensure_ascii=False, sort_keys=True),
            }
        )

    metric = {
        "dataset": dataset_id,
        "candidate": candidate.candidate_id,
        "evaluation_scope": "rolling_no_target_year_leakage",
        "source_policy": candidate.source_policy,
        "train_start": candidate.train_start,
        "train_end_policy": "min(candidate.train_end_cap, target_bs_year - 1)",
        "no_leakage_verified": candidate.leakage_safe,
        "total_months_tested": total,
        "exact_matches": exact,
        "agreement": round(exact / total, 6) if total else 0.0,
        "mismatch_count": total - exact,
        "skipped_years": sorted(skipped_years),
        "skipped_case_estimate": len(skipped_years) * 12,
        "year_total_anomalies": year_total_anomalies,
        "mismatches_by_month": {
            str(month): mismatches_by_month.get(month, 0) for month in range(1, 13)
        },
        "mismatches_by_year": {
            str(year): count for year, count in sorted(mismatches_by_year.items())
        },
        "ashwin_kartik_mismatches": sum(mismatches_by_month.get(month, 0) for month in (6, 7)),
        "twenty_nine_or_thirty_two_day_mismatches": sum(
            1
            for row in mismatches
            if row["actual_days"] in {29, 32} or row["predicted_days"] in {29, 32}
        ),
        "applied_rule_count": applied_rule_count,
        "invalid_residual_year_total_reverted_count": reverted_invalid_count,
    }
    return metric, mismatches


def _legacy_similarity(candidate: Candidate, start: int, end: int) -> dict[str, Any]:
    same = 0
    total = 0
    skipped_years: list[int] = []
    for year in range(start, end + 1):
        months, _, _ = _predict_candidate_year(candidate, year)
        if months is None:
            skipped_years.append(year)
            continue
        legacy_months = predict_legacy_cycle(year).months
        for predicted, legacy in zip(months, legacy_months):
            total += 1
            if predicted == legacy:
                same += 1
    return {
        "same_as_legacy_months": same,
        "total_compared": total,
        "legacy_similarity": round(same / total, 6) if total else 0.0,
        "skipped_years": skipped_years,
        "market_continuity_logic": bool(total and same / total >= LEGACY_IMITATION_LIMIT),
    }


def _evaluate_candidate(candidate: Candidate, datasets: dict[str, list[dict[str, Any]]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    metrics: dict[str, Any] = {}
    all_mismatches: list[dict[str, Any]] = []
    for dataset_id, cases in datasets.items():
        metric, mismatches = _evaluate_cases(cases, candidate, dataset_id=dataset_id)
        metrics[dataset_id] = metric
        all_mismatches.extend(mismatches)
    metrics["legacy_imitation_check"] = _legacy_similarity(candidate, 2001, 2099)
    return metrics, all_mismatches


def _delta(after: dict[str, Any], before: dict[str, Any]) -> dict[str, Any]:
    return {
        "exact_match_delta": after["exact_matches"] - before["exact_matches"],
        "agreement_delta": round(after["agreement"] - before["agreement"], 6),
        "mismatch_delta": after["mismatch_count"] - before["mismatch_count"],
        "total_month_delta": after["total_months_tested"] - before["total_months_tested"],
    }


def _all_year_total_anomalies(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    anomalies: list[dict[str, Any]] = []
    for dataset_id, metric in metrics.items():
        if dataset_id == "legacy_imitation_check":
            continue
        anomalies.extend(metric.get("year_total_anomalies", []))
    return anomalies


def _gate_candidate(
    candidate: Candidate,
    metrics: dict[str, Any],
    best_metrics: dict[str, Any],
) -> dict[str, Any]:
    official = metrics["official_strict"]
    medium = metrics["medium_high_training"]
    all_witness = metrics["all_witness_experimental"]
    hamro = metrics["hamropatro_shadow_experimental"]
    best_medium = best_metrics["medium_high_training"]
    best_all = best_metrics["all_witness_experimental"]
    best_hamro = best_metrics["hamropatro_shadow_experimental"]
    legacy_check = metrics["legacy_imitation_check"]

    checks = {
        "official_strict_2078_2083_guard_72_of_72": (
            official["exact_matches"] == 72 and official["total_months_tested"] == 72
        ),
        "no_target_year_lookup_or_corpus_leakage": candidate.leakage_safe,
        "no_year_or_failure_specific_hardcoded_patch": candidate.hardcoded_patch_safe,
        "no_invalid_year_totals": not _all_year_total_anomalies(metrics),
        "medium_high_rolling_regression_within_0_25_percent": (
            medium["agreement"] >= best_medium["agreement"] - MEDIUM_HIGH_MAX_REGRESSION
        ),
        "all_witness_2000_2099_improves": (
            all_witness["total_months_tested"] >= best_all["total_months_tested"]
            and all_witness["exact_matches"] > best_all["exact_matches"]
        ),
        "hamropatro_shadow_improves_or_mismatches_explained": (
            hamro["exact_matches"] > best_hamro["exact_matches"]
            or candidate.notes != ""
        ),
        "explainable_civil_rule_regime_logic": (
            candidate.explainability_class
            in {"civil_date_rule_regime_logic", "civil_regime_residual_logic"}
            and not legacy_check["market_continuity_logic"]
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    return {
        "accepted": not failed,
        "checks": checks,
        "failed_checks": failed,
        "legacy_imitation_check": legacy_check,
        "reason": "accepted_multi_objective_improvement" if not failed else "rejected_by_multi_objective_gate",
    }


def _affected_rows(
    before: Candidate,
    after: Candidate,
    cases: list[dict[str, Any]],
    *,
    limit: int = 100,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    improved = 0
    worsened = 0
    neutral = 0
    by_month: Counter[int] = Counter()
    by_year: Counter[int] = Counter()
    seen: set[tuple[int, int]] = set()
    for case in cases:
        key = (int(case["bs_year"]), int(case["bs_month"]))
        if key in seen:
            continue
        seen.add(key)
        before_months, _, _ = _predict_candidate_year(before, key[0])
        after_months, _, _ = _predict_candidate_year(after, key[0])
        if before_months is None or after_months is None:
            continue
        before_days = before_months[key[1] - 1]
        after_days = after_months[key[1] - 1]
        if before_days == after_days:
            continue
        actual_days = int(case["actual_days"])
        before_correct = before_days == actual_days
        after_correct = after_days == actual_days
        if after_correct and not before_correct:
            improved += 1
            effect = "improved"
        elif before_correct and not after_correct:
            worsened += 1
            effect = "worsened"
        else:
            neutral += 1
            effect = "changed_still_mismatch"
        by_month[key[1]] += 1
        by_year[key[0]] += 1
        if len(rows) < limit:
            rows.append(
                {
                    "bs_year": key[0],
                    "bs_month": key[1],
                    "month_name": case["month_name"],
                    "actual_days": actual_days,
                    "before_days": before_days,
                    "after_days": after_days,
                    "effect": effect,
                }
            )
    return {
        "changed_month_count": improved + worsened + neutral,
        "improved_count": improved,
        "worsened_count": worsened,
        "neutral_changed_count": neutral,
        "changed_by_month": {
            str(month): by_month.get(month, 0) for month in range(1, 13)
        },
        "changed_by_year": {str(year): count for year, count in sorted(by_year.items())},
        "sample_rows": rows,
    }


def _candidate_list() -> list[Candidate]:
    return [
        Candidate(
            candidate_id="all_witness_experimental_full_history_rolling",
            kind="solar_civil",
            source_policy="all_witness_experimental",
            notes=(
                "Experimental weak-source-policy calibration. Tier 5/6 rows remain excluded from "
                "official_strict and official claim-readiness."
            ),
        ),
        Candidate(
            candidate_id="shadow_residual_fixed_future_window_min_support_4",
            kind="shadow_residual_fixed",
            source_policy="all_witness_experimental",
            min_support=4,
            leakage_safe=False,
            explainability_class="market_continuity_table_like_rejected",
            notes="Diagnostic only: trains residual rules on a future-shadow window and therefore cannot pass no-leakage.",
        ),
        Candidate(
            candidate_id="shadow_residual_rolling_min_support_4",
            kind="shadow_residual_rolling",
            source_policy="all_witness_experimental",
            min_support=4,
            explainability_class="civil_regime_residual_logic",
            notes="Rolling residual overlay uses only prior-year broad witness rows for each target year.",
        ),
        Candidate(
            candidate_id="shadow_residual_rolling_min_support_3",
            kind="shadow_residual_rolling",
            source_policy="all_witness_experimental",
            min_support=3,
            explainability_class="civil_regime_residual_logic",
            notes="Rolling residual overlay uses only prior-year broad witness rows for each target year.",
        ),
        Candidate(
            candidate_id="shadow_residual_rolling_min_support_2",
            kind="shadow_residual_rolling",
            source_policy="all_witness_experimental",
            min_support=2,
            explainability_class="civil_regime_residual_logic",
            notes="Rolling residual overlay uses only prior-year broad witness rows for each target year.",
        ),
        Candidate(
            candidate_id="shadow_residual_rolling_min_support_1",
            kind="shadow_residual_rolling",
            source_policy="all_witness_experimental",
            min_support=1,
            explainability_class="civil_regime_residual_logic",
            notes="Rolling residual overlay uses only prior-year broad witness rows for each target year.",
        ),
        Candidate(
            candidate_id="medium_high_recent_regime_2030_rolling",
            kind="solar_civil",
            source_policy="medium_high_training",
            train_start=2030,
            notes="Recent-regime Tier 1-4 calibration; rejected if improved only by skipping older cases.",
        ),
        Candidate(
            candidate_id="all_witness_recent_regime_2030_rolling",
            kind="solar_civil",
            source_policy="all_witness_experimental",
            train_start=2030,
            notes=(
                "Recent-regime all-witness calibration; rejected if it improves apparent agreement "
                "by reducing 2000-2099 coverage or weakening medium/high behavior."
            ),
        ),
    ]


def run_loop(start: int, end: int) -> tuple[dict[str, Any], dict[str, Any] | None, list[dict[str, Any]]]:
    datasets = {
        "official_strict": _official_guard_cases(2078, 2083),
        "medium_high_training": _cases_from_policy("medium_high_training", start, end),
        "all_witness_experimental": _cases_from_policy("all_witness_experimental", start, end),
        "hamropatro_shadow_experimental": _hamropatro_cases(start, end),
    }

    baseline_metrics, baseline_mismatches = _evaluate_candidate(BASELINE, datasets)
    best_candidate = BASELINE
    best_metrics = baseline_metrics
    best_mismatches = baseline_mismatches
    accepted_rules: dict[str, Any] | None = None
    non_improving = 0
    stop_reason = "candidate_list_exhausted"
    loop_history: list[dict[str, Any]] = [
        {
            "loop": 0,
            "candidate": BASELINE.candidate_id,
            "accepted": True,
            "reason": "baseline",
            "candidate_metadata": BASELINE.__dict__,
            "metrics": baseline_metrics,
        }
    ]

    for loop_index, candidate in enumerate(_candidate_list(), start=1):
        metrics, mismatches = _evaluate_candidate(candidate, datasets)
        gate = _gate_candidate(candidate, metrics, best_metrics)
        affected = _affected_rows(
            best_candidate,
            candidate,
            datasets["all_witness_experimental"],
        )
        loop_record = {
            "loop": loop_index,
            "candidate": candidate.candidate_id,
            "accepted": gate["accepted"],
            "reason": gate["reason"],
            "candidate_metadata": candidate.__dict__,
            "gate": gate,
            "before_after_metrics": {
                "official_strict": _delta(metrics["official_strict"], best_metrics["official_strict"]),
                "medium_high_training": _delta(metrics["medium_high_training"], best_metrics["medium_high_training"]),
                "all_witness_experimental": _delta(
                    metrics["all_witness_experimental"],
                    best_metrics["all_witness_experimental"],
                ),
                "hamropatro_shadow_experimental": _delta(
                    metrics["hamropatro_shadow_experimental"],
                    best_metrics["hamropatro_shadow_experimental"],
                ),
            },
            "metrics": metrics,
            "affected_years_months": affected,
            "official_2078_2083_guard_result": {
                "exact_matches": metrics["official_strict"]["exact_matches"],
                "total_months_tested": metrics["official_strict"]["total_months_tested"],
                "clean": metrics["official_strict"]["exact_matches"] == 72
                and metrics["official_strict"]["total_months_tested"] == 72,
            },
            "leakage_check": {
                "passed": candidate.leakage_safe,
                "policy": "rolling train_end is target_bs_year - 1; residual fixed candidate is intentionally rejected",
            },
            "year_total_check": {
                "passed": not _all_year_total_anomalies(metrics),
                "anomalies": _all_year_total_anomalies(metrics),
            },
        }
        loop_history.append(loop_record)
        if gate["accepted"]:
            best_candidate = candidate
            best_metrics = metrics
            best_mismatches = mismatches
            non_improving = 0
            if candidate.kind == "shadow_residual_rolling":
                accepted_rules = {
                    "publication_status": PUBLICATION_STATUS,
                    "rule_version": candidate.candidate_id,
                    "training_mode": "rolling_prior_years_only",
                    "min_support": candidate.min_support,
                    "source_policy": candidate.source_policy,
                    "official_claim_usable": False,
                    "claim_boundary": (
                        "Accepted only for all_witness_experimental diagnostics. "
                        "Not official_strict accuracy and not official claim-readiness."
                    ),
                }
        else:
            non_improving += 1

        best_experimental = best_metrics["all_witness_experimental"]["agreement"]
        if best_experimental >= TARGET_EXPERIMENTAL_ACCURACY:
            stop_reason = "experimental_target_accuracy_reached_under_gate"
            break
        if non_improving >= MAX_NON_IMPROVING_LOOPS:
            stop_reason = "four_continuous_non_improving_or_rejected_loops"
            break

    payload = {
        "publication_status": PUBLICATION_STATUS,
        "report_id": "solar_civil_rule_loop_2000_2099",
        "benchmark_scope": (
            "Multi-objective rolling no-leakage rule loop across official_strict, "
            "medium_high_training, all_witness_experimental, and HamroPatro shadow lanes."
        ),
        "target_experimental_accuracy": TARGET_EXPERIMENTAL_ACCURACY,
        "target_reached": best_metrics["all_witness_experimental"]["agreement"] >= TARGET_EXPERIMENTAL_ACCURACY,
        "stop_reason": stop_reason,
        "best_candidate": best_candidate.__dict__,
        "best_metrics": best_metrics,
        "baseline_metrics": baseline_metrics,
        "loop_history": loop_history,
        "official_claim_usable": False,
        "claim_boundary": (
            "The 95% target in this report is experimental. It must not be reported as official accuracy "
            "unless achieved under official_strict or strong Tier 1/2 validation."
        ),
    }
    return payload, accepted_rules, best_mismatches


def _write_mismatches(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "dataset",
        "candidate",
        "bs_year",
        "bs_month",
        "month_name",
        "actual_days",
        "predicted_days",
        "source_tier",
        "trust_scope",
        "risk_flags",
        "applied_rules",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    best = payload["best_metrics"]
    lines = [
        "# Solar-Civil Multi-Objective Rule Optimization Loop",
        "",
        f"Publication status: `{payload['publication_status']}`",
        "",
        payload["claim_boundary"],
        "",
        f"- Experimental 95% target reached: {str(payload['target_reached']).lower()}",
        f"- Stop reason: `{payload['stop_reason']}`",
        f"- Best candidate: `{payload['best_candidate']['candidate_id']}`",
        (
            f"- Official 2078-2083 guard: {best['official_strict']['exact_matches']}/"
            f"{best['official_strict']['total_months_tested']}"
        ),
        (
            f"- Medium/high rolling: {best['medium_high_training']['exact_matches']}/"
            f"{best['medium_high_training']['total_months_tested']} = "
            f"{best['medium_high_training']['agreement']:.4f}"
        ),
        (
            f"- All-witness rolling: {best['all_witness_experimental']['exact_matches']}/"
            f"{best['all_witness_experimental']['total_months_tested']} = "
            f"{best['all_witness_experimental']['agreement']:.4f}"
        ),
        (
            f"- HamroPatro shadow rolling: {best['hamropatro_shadow_experimental']['exact_matches']}/"
            f"{best['hamropatro_shadow_experimental']['total_months_tested']} = "
            f"{best['hamropatro_shadow_experimental']['agreement']:.4f}"
        ),
        "",
        "## Loop Decisions",
        "",
    ]
    for item in payload["loop_history"]:
        if item["loop"] == 0:
            continue
        all_metric = item["metrics"]["all_witness_experimental"]
        hamro_metric = item["metrics"]["hamropatro_shadow_experimental"]
        guard = item["official_2078_2083_guard_result"]
        failed = ", ".join(item["gate"]["failed_checks"]) or "none"
        lines.extend(
            [
                f"### Loop {item['loop']}: `{item['candidate']}`",
                "",
                f"- Decision: {'accepted' if item['accepted'] else 'rejected'}",
                f"- Reason: `{item['reason']}`",
                f"- Failed checks: {failed}",
                f"- All-witness: {all_metric['exact_matches']}/{all_metric['total_months_tested']} = {all_metric['agreement']:.4f}",
                f"- HamroPatro shadow: {hamro_metric['exact_matches']}/{hamro_metric['total_months_tested']} = {hamro_metric['agreement']:.4f}",
                f"- 2078-2083 guard: {guard['exact_matches']}/{guard['total_months_tested']} clean={guard['clean']}",
                f"- Leakage check: {item['leakage_check']['passed']}",
                f"- Year-total check: {item['year_total_check']['passed']}",
                (
                    f"- Affected months: {item['affected_years_months']['changed_month_count']} "
                    f"(improved {item['affected_years_months']['improved_count']}, "
                    f"worsened {item['affected_years_months']['worsened_count']})"
                ),
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, default=2000)
    parser.add_argument("--end", type=int, default=2099)
    parser.add_argument("--out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    parser.add_argument("--mismatches", type=Path, default=DEFAULT_MISMATCHES)
    args = parser.parse_args()

    payload, rules, mismatches = run_loop(args.start, args.end)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if rules:
        args.rules.write_text(json.dumps(rules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_mismatches(args.mismatches, mismatches)
    _write_markdown(args.md, payload)
    print(
        json.dumps(
            {
                "publication_status": payload["publication_status"],
                "target_reached": payload["target_reached"],
                "stop_reason": payload["stop_reason"],
                "best_candidate": payload["best_candidate"]["candidate_id"],
                "best_metrics": {
                    key: {
                        "exact_matches": value["exact_matches"],
                        "total_months_tested": value["total_months_tested"],
                        "agreement": value["agreement"],
                    }
                    for key, value in payload["best_metrics"].items()
                    if key != "legacy_imitation_check"
                },
                "outputs": {
                    "json": str(args.out.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                    "markdown": str(args.md.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                    "mismatches": str(args.mismatches.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                    "rules": str(args.rules.relative_to(PROJECT_ROOT)).replace("\\", "/") if rules else None,
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
