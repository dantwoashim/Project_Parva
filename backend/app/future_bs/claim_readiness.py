"""Claim-readiness reporting for future BS accuracy statements."""

from __future__ import annotations

from typing import Any

from .accuracy import TARGET_THRESHOLDS
from .active_learning_queue import write_active_learning_queue
from .backtest import backtest_model
from .corpus import corpus_summary
from .models import CALIBRATION_VERSION, METHOD_VERSION
from .precomputed_store import load_precomputed_predictions
from .year_total_gate import year_total_gate


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


def claim_readiness_report() -> dict[str, Any]:
    corpus = corpus_summary()
    official_cases = int(corpus["final_test_allowed_month_cases"])
    minimum_cases = int(corpus["minimum_final_claim_month_cases"])
    strict = backtest_model(2000, 2077, 2078, 2083, source_policy="official_only")
    metrics = strict["accuracy_metrics"]
    invalid_totals = _invalid_future_year_totals()
    false_green_rate = max(0.0, round((100.0 - float(metrics["green_zone_accuracy"])) / 100.0, 6))
    ready = (
        official_cases >= minimum_cases
        and invalid_totals["count"] == 0
        and float(metrics["green_zone_accuracy"]) >= TARGET_THRESHOLDS["green_zone_accuracy"]
        and float(metrics["green_zone_coverage"]) >= TARGET_THRESHOLDS["green_zone_coverage"]
        and float(metrics["overall_top1_accuracy"]) >= TARGET_THRESHOLDS["overall_top1_accuracy"]
        and false_green_rate <= 0.005
    )
    blockers = []
    if official_cases < minimum_cases:
        blockers.append(
            f"official/printed final-test corpus has {official_cases} month cases; target is {minimum_cases}"
        )
    if not ready and not blockers:
        blockers.append("accuracy or coverage threshold not met")
    if invalid_totals["count"]:
        blockers.append(f"{invalid_totals['count']} future BS years have invalid/exceptional totals")
    safe_claims = [
        "Parva provides computed predictions, not official future publication.",
        "Parva can separate high-confidence months from risky months.",
        "Parva can audit an external future BS month-length sheet.",
        "Parva can estimate financial exposure of one-day mismatches.",
    ]
    active_queue = write_active_learning_queue()
    unsafe_claims = [
        "Parva guarantees official future calendar to 2200 BS.",
        "Parva replaces the Panchanga Nirnayak Samiti.",
        "Parva's future predictions are official.",
    ]
    return {
        "claim_ready_99_green_zone": ready,
        "claim_ready_99_overall": False,
        "official_cases": official_cases,
        "required_official_cases": minimum_cases,
        "official_only_top1_accuracy": metrics["overall_top1_accuracy"],
        "green_zone_accuracy": metrics["green_zone_accuracy"],
        "green_zone_coverage": metrics["green_zone_coverage"],
        "false_green_rate": false_green_rate,
        "invalid_future_year_totals": invalid_totals,
        "active_learning_queue": {
            "path": "data/future_bs/corpus/active_learning_queue.csv",
            "rows": len(active_queue),
        },
        "claim_blockers": blockers,
        "safe_claims": safe_claims,
        "unsafe_claims": unsafe_claims,
        "ready_for_blanket_99_percent_claim": False,
        "ready_for_99_percent_green_zone_claim": ready,
        "publication_status_required": "computed_prediction_not_official",
        "safe_claim": (
            "Parva provides computed future BS month-length predictions with source-labeled "
            "confidence, risk flags, and claim-gated accuracy reporting."
        ),
        "disallowed_claims": unsafe_claims,
        "blockers": blockers,
        "corpus": corpus,
        "strict_official_holdout": metrics,
        "method_version": METHOD_VERSION,
        "calibration_version": CALIBRATION_VERSION,
    }
