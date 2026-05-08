"""Artifact-first claim-readiness reporting for future BS accuracy statements."""

from __future__ import annotations

import os
from typing import Any

from .accuracy import TARGET_THRESHOLDS
from .accuracy_objective import objective_from_counts
from .active_learning_queue import write_active_learning_queue
from .backtest import backtest_model
from .corpus import corpus_summary
from .models import CALIBRATION_VERSION, METHOD_VERSION
from .precomputed_store import load_precomputed_predictions
from .report_store import load_report, report_exists
from .year_total_gate import year_total_gate


def _live_compute_enabled() -> bool:
    return os.getenv("PARVA_FUTURE_BS_LIVE_COMPUTE", "0").strip().lower() in {"1", "true", "yes"}


def _invalid_future_year_totals() -> dict[str, Any]:
    payload = load_precomputed_predictions()
    invalid = []
    for year, row in sorted(payload.get("years", {}).items()):
        months = row.get("months") or []
        if not months:
            continue
        gate = year_total_gate([int(value) for value in months])
        if not gate["valid_future_year_total"]:
            invalid.append(
                {
                    "bs_year": int(year),
                    "total_days": gate["year_total_days"],
                    "risk_label": "RED",
                    "claimable": False,
                    "manual_review_required": True,
                    "reason": "invalid_or_exceptional_year_total",
                }
            )
    return {"count": len(invalid), "years": invalid}


def _safe_claims() -> list[str]:
    return [
        "Parva provides computed predictions, not official future publication.",
        "Parva can separate high-confidence months from risky months.",
        "Parva can audit an external future BS month-length sheet.",
        "Parva can estimate operational exposure of one-day mismatches.",
    ]


def _unsafe_claims() -> list[str]:
    return [
        "Parva guarantees official future calendar to 2200 BS.",
        "Parva replaces the Panchanga Nirnayak Samiti.",
        "Parva's future predictions are official.",
        "Parva has claim-ready 99%+ accuracy without sufficient verified source cases.",
    ]


def _normalize_report(payload: dict[str, Any]) -> dict[str, Any]:
    corpus = corpus_summary()
    official_cases = int(payload.get("official_cases", corpus["final_test_allowed_month_cases"]))
    required_cases = int(payload.get("required_official_cases", corpus["minimum_final_claim_month_cases"]))
    invalid_totals = payload.get("invalid_future_year_totals") or _invalid_future_year_totals()
    metrics = {
        "overall_top1_accuracy": float(
            payload.get("overall_top1_accuracy", payload.get("official_only_top1_accuracy", 0.0))
        ),
        "green_zone_accuracy": float(payload.get("green_zone_accuracy", 0.0)),
        "green_zone_coverage": float(payload.get("green_zone_coverage", 0.0)),
        "false_green_rate": float(payload.get("false_green_rate", 1.0)),
        "wrong_green_count": int(payload.get("wrong_green_count", 0) or 0),
    }
    metric_threshold_passed = bool(
        metrics["overall_top1_accuracy"] >= TARGET_THRESHOLDS["overall_top1_accuracy"]
        and metrics["green_zone_accuracy"] >= 99.0
        and metrics["green_zone_coverage"] >= 85.0
        and metrics["false_green_rate"] <= 0.005
        and metrics["wrong_green_count"] == 0
        and int(invalid_totals.get("count", 0)) == 0
    )
    claim_ready_with_sufficient_corpus = bool(official_cases >= required_cases)
    claim_ready_green = bool(metric_threshold_passed and claim_ready_with_sufficient_corpus)
    blockers = list(payload.get("claim_blockers") or payload.get("blockers") or [])
    if not claim_ready_with_sufficient_corpus:
        blocker = f"official/printed final-test corpus has {official_cases} month cases; target is {required_cases}"
        if blocker not in blockers:
            blockers.append(blocker)
    if int(invalid_totals.get("count", 0)):
        blocker = f"{invalid_totals['count']} future BS years have invalid/exceptional totals"
        if blocker not in blockers:
            blockers.append(blocker)
    deduped_blockers: list[str] = []
    for blocker in blockers:
        if blocker not in deduped_blockers:
            deduped_blockers.append(blocker)
    blockers = deduped_blockers
    normalized = {
        **payload,
        "metric_threshold_passed": metric_threshold_passed,
        "claim_ready_with_sufficient_corpus": claim_ready_with_sufficient_corpus,
        "claim_ready_99_green_zone": claim_ready_green,
        "claim_ready_99_overall": False,
        "official_cases": official_cases,
        "required_official_cases": required_cases,
        "overall_top1_accuracy": metrics["overall_top1_accuracy"],
        "official_only_top1_accuracy": metrics["overall_top1_accuracy"],
        "green_zone_accuracy": metrics["green_zone_accuracy"],
        "green_zone_coverage": metrics["green_zone_coverage"],
        "false_green_rate": metrics["false_green_rate"],
        "wrong_green_count": metrics["wrong_green_count"],
        "invalid_future_year_totals": invalid_totals,
        "claim_blockers": blockers,
        "blockers": blockers,
        "safe_claims": payload.get("safe_claims") or _safe_claims(),
        "unsafe_claims": payload.get("unsafe_claims") or _unsafe_claims(),
        "ready_for_blanket_99_percent_claim": False,
        "ready_for_99_percent_green_zone_claim": claim_ready_green,
        "publication_status_required": "computed_prediction_not_official",
        "publication_status": "computed_prediction_not_official",
        "corpus": payload.get("corpus") or corpus,
        "method_version": payload.get("method_version", METHOD_VERSION),
        "calibration_version": payload.get("calibration_version", CALIBRATION_VERSION),
    }
    return normalized


def _artifact_report() -> dict[str, Any] | None:
    if report_exists("claim_readiness_v_final"):
        return load_report("claim_readiness_v_final")
    if report_exists("external_audit_readiness_summary"):
        return load_report("external_audit_readiness_summary")
    readiness = load_report("claim_readiness_v_final")
    if readiness.get("error"):
        return None
    return readiness


def _accuracy_lab_report() -> dict[str, Any] | None:
    paths = [
        ("data/future_bs/accuracy_lab/accuracy_readiness_final.json", "readiness"),
        ("data/future_bs/accuracy_lab/best_metrics.json", "metrics"),
    ]
    from .report_store import PROJECT_ROOT

    loaded: dict[str, Any] = {}
    for relative, key in paths:
        path = PROJECT_ROOT / relative
        if path.exists() and path.stat().st_size > 0:
            import json

            loaded[key] = json.loads(path.read_text(encoding="utf-8"))
    if not loaded:
        return None
    payload = {**loaded.get("readiness", {}), **loaded.get("metrics", {})}
    return payload


def _live_report() -> dict[str, Any]:
    corpus = corpus_summary()
    official_cases = int(corpus["final_test_allowed_month_cases"])
    required_cases = int(corpus["minimum_final_claim_month_cases"])
    strict = backtest_model(2000, 2077, 2078, 2083, source_policy="official_only")
    metrics = strict["accuracy_metrics"]
    objective = objective_from_counts(
        total_cases=int(metrics["total_month_cases"]),
        top1_correct=int(metrics["passed_month_cases"]),
        green_cases=int(metrics["green_zone_cases"]),
        green_correct=int(metrics["green_zone_passed"]),
        invalid_future_years=_invalid_future_year_totals()["count"],
        future_years=len(load_precomputed_predictions().get("years", {})),
        mismatch_count=int(metrics["failed_month_cases"]),
    )
    return {
        **objective,
        "official_cases": official_cases,
        "required_official_cases": required_cases,
        "invalid_future_year_totals": _invalid_future_year_totals(),
        "claim_blockers": [],
        "safe_claims": _safe_claims(),
        "unsafe_claims": _unsafe_claims(),
        "corpus": corpus,
        "strict_official_holdout": metrics,
        "publication_status": "computed_prediction_not_official",
    }


def claim_readiness_report(*, force_recompute: bool = False) -> dict[str, Any]:
    """Return claim readiness without live backtest unless explicitly requested."""

    if force_recompute or _live_compute_enabled():
        payload = _live_report()
    else:
        payload = _artifact_report() or _accuracy_lab_report() or {}
    if not payload:
        payload = {
            "overall_top1_accuracy": 0.0,
            "green_zone_accuracy": 0.0,
            "green_zone_coverage": 0.0,
            "false_green_rate": 1.0,
            "wrong_green_count": 0,
        }
    normalized = _normalize_report(payload)
    active_queue = write_active_learning_queue()
    normalized["active_learning_queue"] = {
        "path": "data/future_bs/corpus/active_learning_queue.csv",
        "rows": len(active_queue),
    }
    return normalized
