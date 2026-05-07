"""Claim-readiness reporting for future BS accuracy statements."""

from __future__ import annotations

from typing import Any

from .accuracy import TARGET_THRESHOLDS
from .backtest import backtest_model
from .corpus import corpus_summary
from .models import CALIBRATION_VERSION, METHOD_VERSION


def claim_readiness_report() -> dict[str, Any]:
    corpus = corpus_summary()
    official_cases = int(corpus["final_test_allowed_month_cases"])
    minimum_cases = int(corpus["minimum_final_claim_month_cases"])
    strict = backtest_model(2000, 2077, 2078, 2083, source_policy="official_only")
    metrics = strict["accuracy_metrics"]
    ready = (
        official_cases >= minimum_cases
        and float(metrics["green_zone_accuracy"]) >= TARGET_THRESHOLDS["green_zone_accuracy"]
        and float(metrics["green_zone_coverage"]) >= TARGET_THRESHOLDS["green_zone_coverage"]
        and float(metrics["overall_top1_accuracy"]) >= TARGET_THRESHOLDS["overall_top1_accuracy"]
    )
    blockers = []
    if official_cases < minimum_cases:
        blockers.append(
            f"official/printed final-test corpus has {official_cases} month cases; target is {minimum_cases}"
        )
    if not ready and not blockers:
        blockers.append("accuracy or coverage threshold not met")
    return {
        "ready_for_blanket_99_percent_claim": False,
        "ready_for_99_percent_green_zone_claim": ready,
        "publication_status_required": "computed_prediction_not_official",
        "safe_claim": (
            "Parva provides computed future BS month-length predictions with source-labeled "
            "confidence, risk flags, and claim-gated accuracy reporting."
        ),
        "disallowed_claims": [
            "Parva guarantees official future Nepali calendar accuracy to 2200 BS.",
            "Parva replaces Panchanga Nirnayak Samiti.",
            "Third-party future rows are official evidence.",
        ],
        "blockers": blockers,
        "corpus": corpus,
        "strict_official_holdout": metrics,
        "method_version": METHOD_VERSION,
        "calibration_version": CALIBRATION_VERSION,
    }
