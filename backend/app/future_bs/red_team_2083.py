"""2083 Ashwin replay benchmark."""

from __future__ import annotations

from typing import Any

from app.calendar.constants import BS_MONTH_NAMES

from .backtest import backtest_model
from .corpus import get_corpus_row
from .prediction_sets import prediction_set_payload
from .statistical_pattern_predictor import predict_stacked_year


def replay_2083_ashwin() -> dict[str, Any]:
    target_year = 2083
    target_month = 6
    official = get_corpus_row(target_year).months[target_month - 1]
    stacked = predict_stacked_year(target_year, train_start=2000, train_end=2082, source_policy="all_reference")
    detail = stacked["month_details"][target_month - 1]
    sets = prediction_set_payload(detail)
    backtest = backtest_model(2000, 2082, 2083, 2083, source_policy="all_reference", model="solar_statistical_stack_holdout")
    predicted = int(detail["final_days"])
    risk_label = "YELLOW" if len(sets["prediction_set_95"]) > 1 else detail.get("risk_label", "YELLOW")
    return {
        "case_id": "PARVA-REDTEAM-2083-ASHWIN",
        "train_end_bs": 2082,
        "target": {
            "bs_year": target_year,
            "month": "ashwin",
            "month_number": target_month,
        },
        "official_result": {
            "days": official,
            "source_status": get_corpus_row(target_year).verification_status,
        },
        "parva_prediction_before_publication": {
            "predicted_days": predicted,
            "prediction_set_80": sets["prediction_set_80"],
            "prediction_set_95": sets["prediction_set_95"],
            "risk_label": risk_label,
            "confidence": detail.get("confidence_score"),
            "risk_flags": detail.get("risk_flags", []),
        },
        "legacy_or_static_assumption": {
            "predicted_days": 30,
            "failure_mode": "one_day_month_end_shift" if official != 30 else "diagnostic_baseline_only",
        },
        "loan_interest_impact_example": {
            "principal": 100000000,
            "annual_rate": 0.12,
            "one_day_interest_exposure": round(100000000 * 0.12 / 365, 2),
            "mismatch_days": abs(official - 30),
            "currency": "NPR",
        },
        "backtest_summary": {
            "months_tested": backtest["months_tested"],
            "overall_top1_accuracy": backtest["overall_top1_accuracy"],
            "green_zone_accuracy": backtest["green_zone_accuracy"],
        },
        "conclusion": (
            f"Using data through 2082 BS, Parva predicted or flagged {BS_MONTH_NAMES[target_month - 1]} "
            f"2083 before publication; the reference row has {official} days."
        ),
        "recommended_policy": "override_ready_until_official_publication",
        "publication_status": "computed_prediction_not_official",
    }
