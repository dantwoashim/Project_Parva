#!/usr/bin/env python3
"""Compare old and current solar-civil rule stacks across available witnesses."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
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
from app.research.future_bs.models import MONTH_DAY_VALUES  # noqa: E402
from app.research.future_bs.solar_ingress_predictor import (  # noqa: E402
    CALIBRATED_RECENT_RULE,
    CALIBRATED_REFERENCE_RULE,
    CIVIL_DECISION_KNN_RULE,
    PREDICTION_RULES,
    calibrated_rule_weights,
    predict_solar_ingress_year,
    predict_with_rule,
)
from app.research.future_bs.source_policy import PUBLICATION_STATUS, policy_rows  # noqa: E402

OUT_DIR = PROJECT_ROOT / "data" / "future_bs" / "accuracy_lab"
DEFAULT_JSON = OUT_DIR / "solar_civil_before_after_2000_2099_metrics.json"
DEFAULT_MD = OUT_DIR / "solar_civil_before_after_2000_2099_metrics.md"
DEFAULT_CSV = OUT_DIR / "solar_civil_before_after_2000_2099_mismatches.csv"

BEFORE_MODE = {
    "id": "before_old_knn_threshold_selector",
    "description": "Emulates previous behavior: KNN ran alone when its calibrated score was >= 0.85.",
    "source_policy": "all_reference",
    "train_start": 2050,
    "train_end": 2083,
}

AFTER_MODE = {
    "id": "after_reconstructed_rules_dominance_sequence_guard",
    "description": (
        "Current behavior: reconstructed medium/high training rows, KNN dominance gate, "
        "and whole-year sequence guard."
    ),
    "source_policy": "medium_high_training",
    "train_start": 2050,
    "train_end": 2083,
}


def _load_hamropatro_years() -> dict[int, list[int]]:
    payload = json.loads(HAMROPATRO_MONTH_LENGTHS_PATH.read_text(encoding="utf-8"))
    years: dict[int, list[int]] = {}
    for row in payload.get("years", []):
        year = int(row["bs_year"])
        months = [int(month["days"]) for month in row["months"]]
        if len(months) == 12:
            years[year] = months
    return years


def _case(
    *,
    dataset_id: str,
    bs_year: int,
    bs_month: int,
    actual_days: int,
    source_type: str,
    source_tier: str,
    trust_scope: str,
) -> dict[str, Any]:
    return {
        "dataset_id": dataset_id,
        "bs_year": bs_year,
        "bs_month": bs_month,
        "month_name": BS_MONTH_NAMES[bs_month - 1],
        "actual_days": actual_days,
        "source_type": source_type,
        "source_tier": source_tier,
        "trust_scope": trust_scope,
    }


def _hamropatro_cases(start: int, end: int) -> list[dict[str, Any]]:
    years = _load_hamropatro_years()
    cases: list[dict[str, Any]] = []
    for year in range(start, end + 1):
        months = years.get(year)
        if not months:
            continue
        for month, days in enumerate(months, start=1):
            cases.append(
                _case(
                    dataset_id="hamropatro_shadow_2000_2099",
                    bs_year=year,
                    bs_month=month,
                    actual_days=days,
                    source_type="third_party_reference",
                    source_tier="6",
                    trust_scope="shadow_agreement_not_official_accuracy",
                )
            )
    return cases


def _verified_corpus_cases(start: int, end: int) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for row in corpus_rows():
        if not start <= row.bs_year <= end:
            continue
        for month, days in enumerate(row.months, start=1):
            cases.append(
                _case(
                    dataset_id="verified_month_lengths_all_reference_2000_2099",
                    bs_year=row.bs_year,
                    bs_month=month,
                    actual_days=days,
                    source_type=row.source_type,
                    source_tier=str(row.source_quality_level),
                    trust_scope="mixed_source_reference_not_official_strict",
                )
            )
    return cases


def _reconstructed_policy_cases(policy: str, start: int, end: int) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for row in policy_rows(policy):
        year = int(row["bs_year"])
        if not start <= year <= end:
            continue
        cases.append(
            _case(
                dataset_id=f"reconstructed_{policy}_2000_2099",
                bs_year=year,
                bs_month=int(row["bs_month"]),
                actual_days=int(row["month_length"]),
                source_type=row.get("verification_status", ""),
                source_tier=str(row.get("best_source_tier", "")),
                trust_scope=policy,
            )
        )
    return cases


def _datasets(start: int, end: int) -> dict[str, list[dict[str, Any]]]:
    return {
        "hamropatro_shadow_2000_2099": _hamropatro_cases(start, end),
        "verified_month_lengths_all_reference_2000_2099": _verified_corpus_cases(start, end),
        "reconstructed_all_witness_experimental_2000_2099": _reconstructed_policy_cases(
            "all_witness_experimental",
            start,
            end,
        ),
        "reconstructed_medium_high_training_2000_2099": _reconstructed_policy_cases(
            "medium_high_training",
            start,
            end,
        ),
        "reconstructed_official_strict_2000_2099": _reconstructed_policy_cases(
            "official_strict",
            start,
            end,
        ),
    }


def _old_selected_prediction_rules(weights: dict[str, float]) -> list[str]:
    knn_score = weights.get(CIVIL_DECISION_KNN_RULE, 0.0)
    if knn_score >= 0.85:
        return [CIVIL_DECISION_KNN_RULE]
    ranked = sorted(weights.items(), key=lambda row: row[1], reverse=True)
    if not ranked:
        return list(PREDICTION_RULES)
    best_score = ranked[0][1]
    selected = [
        rule_name
        for rule_name, score in ranked
        if score >= max(0.80, best_score - 0.08)
    ][:5]
    for required in (CIVIL_DECISION_KNN_RULE, CALIBRATED_RECENT_RULE, CALIBRATED_REFERENCE_RULE):
        if required in weights and required not in selected and len(selected) < 5:
            selected.append(required)
    return selected or [ranked[0][0]]


@lru_cache(maxsize=1024)
def _predict_before(bs_year: int, train_start: int, train_end: int) -> tuple[int, ...]:
    weights = calibrated_rule_weights(
        train_start,
        train_end,
        source_policy=BEFORE_MODE["source_policy"],
    )
    selected = _old_selected_prediction_rules(weights)
    outputs = [
        predict_with_rule(
            bs_year,
            rule_name,
            rule_weight=weights[rule_name],
            train_start=train_start,
            train_end=train_end,
            source_policy=BEFORE_MODE["source_policy"],
        )
        for rule_name in selected
    ]
    final_months: list[int] = []
    for month_index in range(12):
        weighted_votes: Counter[int] = Counter()
        raw_votes: Counter[int] = Counter()
        for output in outputs:
            days = output.months[month_index]
            weighted_votes[days] += output.rule_weight
            raw_votes[days] += 1
        final_months.append(max(MONTH_DAY_VALUES, key=lambda days: (weighted_votes[days], raw_votes[days])))
    return tuple(final_months)


@lru_cache(maxsize=1024)
def _predict_after(bs_year: int, train_start: int, train_end: int) -> tuple[int, ...]:
    return tuple(
        predict_solar_ingress_year(
            bs_year,
            train_start=train_start,
            train_end=train_end,
            source_policy=AFTER_MODE["source_policy"],
        )["months"]
    )


def _effective_train_end(mode: dict[str, Any], bs_year: int, evaluation_scope: str) -> int | None:
    if evaluation_scope == "retrospective_fixed_train_window":
        return int(mode["train_end"])
    if evaluation_scope == "rolling_pre_publication":
        if bs_year <= int(mode["train_start"]):
            return None
        return min(int(mode["train_end"]), bs_year - 1)
    raise ValueError(f"Unknown evaluation scope: {evaluation_scope}")


def _predict(mode: str, bs_year: int, train_end: int) -> tuple[int, ...]:
    if mode == "before":
        return _predict_before(bs_year, BEFORE_MODE["train_start"], train_end)
    if mode == "after":
        return _predict_after(bs_year, AFTER_MODE["train_start"], train_end)
    raise ValueError(f"Unknown mode: {mode}")


def _evaluate_cases(
    cases: list[dict[str, Any]],
    *,
    mode_name: str,
    mode: dict[str, Any],
    evaluation_scope: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    total = 0
    exact = 0
    skipped_years: set[int] = set()
    mismatches: list[dict[str, Any]] = []
    mismatches_by_month: Counter[int] = Counter()
    mismatches_by_year: Counter[int] = Counter()
    year_total_anomalies: list[dict[str, Any]] = []
    predictions_by_year: dict[int, tuple[int, ...]] = {}
    year_source_scope: dict[int, set[int]] = defaultdict(set)

    for case in cases:
        year = int(case["bs_year"])
        train_end = _effective_train_end(mode, year, evaluation_scope)
        if train_end is None:
            skipped_years.add(year)
            continue
        if year not in predictions_by_year:
            predicted = _predict(mode_name, year, train_end)
            predictions_by_year[year] = predicted
            if sum(predicted) not in {365, 366}:
                year_total_anomalies.append(
                    {
                        "bs_year": year,
                        "predicted_total": sum(predicted),
                        "mode": mode["id"],
                        "evaluation_scope": evaluation_scope,
                    }
                )
        predicted_days = predictions_by_year[year][int(case["bs_month"]) - 1]
        year_source_scope[year].add(int(case["bs_month"]))
        total += 1
        if predicted_days == int(case["actual_days"]):
            exact += 1
            continue
        mismatches_by_month[int(case["bs_month"])] += 1
        mismatches_by_year[year] += 1
        mismatches.append(
            {
                "evaluation_scope": evaluation_scope,
                "mode": mode["id"],
                "dataset_id": case["dataset_id"],
                "bs_year": year,
                "bs_month": int(case["bs_month"]),
                "month_name": case["month_name"],
                "actual_days": int(case["actual_days"]),
                "predicted_days": predicted_days,
                "source_type": case["source_type"],
                "source_tier": case["source_tier"],
                "trust_scope": case["trust_scope"],
            }
        )

    summary = {
        "mode": mode["id"],
        "mode_description": mode["description"],
        "evaluation_scope": evaluation_scope,
        "source_policy": mode["source_policy"],
        "train_start": mode["train_start"],
        "train_end_cap": mode["train_end"],
        "total_months_tested": total,
        "exact_matches": exact,
        "agreement": round(exact / total, 6) if total else 0.0,
        "mismatch_count": total - exact,
        "years_with_cases": len(year_source_scope),
        "skipped_years": sorted(skipped_years),
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
        "year_total_anomalies": year_total_anomalies,
    }
    return summary, mismatches


def _delta(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    return {
        "agreement_delta": round(after["agreement"] - before["agreement"], 6),
        "exact_match_delta": after["exact_matches"] - before["exact_matches"],
        "mismatch_delta": after["mismatch_count"] - before["mismatch_count"],
        "year_total_anomaly_delta": len(after["year_total_anomalies"]) - len(before["year_total_anomalies"]),
    }


def run_comparison(start: int, end: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    dataset_cases = _datasets(start, end)
    scopes = ["retrospective_fixed_train_window", "rolling_pre_publication"]
    comparisons: dict[str, Any] = {}
    all_mismatches: list[dict[str, Any]] = []

    for dataset_id, cases in dataset_cases.items():
        comparisons[dataset_id] = {
            "case_count": len(cases),
            "source_tier_distribution": dict(Counter(str(case["source_tier"]) for case in cases)),
            "trust_scope_distribution": dict(Counter(str(case["trust_scope"]) for case in cases)),
            "scopes": {},
        }
        for scope in scopes:
            before, before_mismatches = _evaluate_cases(
                cases,
                mode_name="before",
                mode=BEFORE_MODE,
                evaluation_scope=scope,
            )
            after, after_mismatches = _evaluate_cases(
                cases,
                mode_name="after",
                mode=AFTER_MODE,
                evaluation_scope=scope,
            )
            comparisons[dataset_id]["scopes"][scope] = {
                "before": before,
                "after": after,
                "delta": _delta(before, after),
            }
            all_mismatches.extend(before_mismatches)
            all_mismatches.extend(after_mismatches)

    payload = {
        "publication_status": PUBLICATION_STATUS,
        "report_id": "solar_civil_before_after_2000_2099",
        "range": {"start_bs_year": start, "end_bs_year": end},
        "claim_scope": (
            "Diagnostic/shadow comparison only. HamroPatro and mixed-source reconstructed results are not official accuracy."
        ),
        "before_mode": BEFORE_MODE,
        "after_mode": AFTER_MODE,
        "comparisons": comparisons,
    }
    return payload, all_mismatches


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "evaluation_scope",
        "mode",
        "dataset_id",
        "bs_year",
        "bs_month",
        "month_name",
        "actual_days",
        "predicted_days",
        "source_type",
        "source_tier",
        "trust_scope",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Solar-Civil Before/After Comparison 2000-2099",
        "",
        f"Publication status: `{payload['publication_status']}`",
        "",
        payload["claim_scope"],
        "",
        "## Modes",
        "",
        f"- Before: `{payload['before_mode']['id']}` - {payload['before_mode']['description']}",
        f"- After: `{payload['after_mode']['id']}` - {payload['after_mode']['description']}",
        "",
        "## Summary",
        "",
    ]
    for dataset_id, data in payload["comparisons"].items():
        lines.append(f"### {dataset_id}")
        lines.append("")
        lines.append(f"- Case count: {data['case_count']}")
        for scope, scoped in data["scopes"].items():
            before = scoped["before"]
            after = scoped["after"]
            delta = scoped["delta"]
            lines.append(
                f"- {scope}: before {before['exact_matches']}/{before['total_months_tested']} "
                f"= {before['agreement']:.4f}; after {after['exact_matches']}/{after['total_months_tested']} "
                f"= {after['agreement']:.4f}; delta {delta['agreement_delta']:+.4f}"
            )
            if before["year_total_anomalies"] or after["year_total_anomalies"]:
                lines.append(
                    f"  - year-total anomalies: before {len(before['year_total_anomalies'])}, "
                    f"after {len(after['year_total_anomalies'])}"
                )
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, default=2000)
    parser.add_argument("--end", type=int, default=2099)
    parser.add_argument("--out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--mismatches", type=Path, default=DEFAULT_CSV)
    args = parser.parse_args()

    payload, mismatches = run_comparison(args.start, args.end)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_markdown(args.md, payload)
    _write_csv(args.mismatches, mismatches)

    printable = {
        "publication_status": payload["publication_status"],
        "report_id": payload["report_id"],
        "outputs": {
            "json": str(args.out.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "markdown": str(args.md.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "mismatches": str(args.mismatches.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        },
        "summary": {
            dataset_id: {
                scope: scoped["delta"]
                for scope, scoped in dataset["scopes"].items()
            }
            for dataset_id, dataset in payload["comparisons"].items()
        },
    }
    print(json.dumps(printable, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
