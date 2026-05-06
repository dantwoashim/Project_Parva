"""Backtesting for future BS computational and legacy predictors."""

from __future__ import annotations

from typing import Any

from app.calendar.constants import BS_MAX_YEAR, BS_MIN_YEAR, BS_MONTH_LENGTHS, BS_MONTH_NAMES

from .legacy_cycle_predictor import predict_from_training
from .models import CALIBRATION_VERSION, METHOD_VERSION
from .solar_ingress_predictor import predict_solar_ingress_year


def _match_count(predicted: list[int], actual: list[int]) -> int:
    return sum(predicted_days == actual_days for predicted_days, actual_days in zip(predicted, actual))


def _validate_backtest_range(train_start: int, train_end: int, test_start: int, test_end: int) -> None:
    if train_start > train_end or test_start > test_end:
        raise ValueError("Training and test ranges must be ascending.")
    for year in (train_start, train_end, test_start, test_end):
        if year not in BS_MONTH_LENGTHS:
            raise ValueError(
                f"Backtest year {year} is outside the static corpus range {BS_MIN_YEAR}-{BS_MAX_YEAR}."
            )
    if train_end >= test_start:
        raise ValueError("train_end must be earlier than test_start.")


def backtest_model(train_start: int, train_end: int, test_start: int, test_end: int) -> dict[str, Any]:
    _validate_backtest_range(train_start, train_end, test_start, test_end)

    exact_matches = 0
    legacy_exact_matches = 0
    months_tested = 0
    mismatches: list[dict[str, Any]] = []
    yearly_predictions: list[dict[str, Any]] = []

    for year in range(test_start, test_end + 1):
        solar = predict_solar_ingress_year(year, train_start=train_start, train_end=train_end)
        legacy_months, legacy_models = predict_from_training(year, train_start, train_end)
        actual = BS_MONTH_LENGTHS[year]
        solar_matches = _match_count(solar["months"], actual)
        legacy_matches = _match_count(legacy_months, actual)
        exact_matches += solar_matches
        legacy_exact_matches += legacy_matches
        months_tested += 12
        for index, (predicted_days, actual_days) in enumerate(zip(solar["months"], actual), start=1):
            if predicted_days != actual_days:
                mismatches.append(
                    {
                        "bs_year": year,
                        "month": index,
                        "month_name": BS_MONTH_NAMES[index - 1],
                        "predicted_days": predicted_days,
                        "actual_days": actual_days,
                    }
                )
        yearly_predictions.append(
            {
                "bs_year": year,
                "predicted": solar["months"],
                "actual": actual,
                "matches": solar_matches,
                "accuracy": round((solar_matches / 12) * 100, 2),
                "legacy_predicted": legacy_months,
                "legacy_accuracy": round((legacy_matches / 12) * 100, 2),
                "models": [
                    {
                        "model": output["model"],
                        "model_family": "computational_solar_ingress",
                        "rule_weight": output["rule_weight"],
                    }
                    for output in solar["model_outputs"]
                ],
                "legacy_models": legacy_models,
            }
        )

    return {
        "train_range": f"{train_start}-{train_end} BS",
        "test_range": f"{test_start}-{test_end} BS",
        "mode": "computational_solar_ingress_holdout",
        "months_tested": months_tested,
        "exact_matches": exact_matches,
        "mismatches": len(mismatches),
        "accuracy": round((exact_matches / months_tested) * 100, 2) if months_tested else 0.0,
        "legacy_exact_matches": legacy_exact_matches,
        "legacy_accuracy": round((legacy_exact_matches / months_tested) * 100, 2) if months_tested else 0.0,
        "yearly_predictions": yearly_predictions,
        "mismatch_details": mismatches,
        "method_version": METHOD_VERSION,
        "calibration_version": CALIBRATION_VERSION,
        "note": "Solar-ingress backtest is a computational validation aid, not official future publication.",
    }
