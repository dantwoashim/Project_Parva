"""Objective scoring for future BS model selection."""

from __future__ import annotations

from typing import Any


def _rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def objective_from_counts(
    *,
    total_cases: int,
    top1_correct: int,
    green_cases: int,
    green_correct: int,
    invalid_future_years: int = 0,
    future_years: int = 0,
    mismatch_count: int | None = None,
) -> dict[str, Any]:
    wrong_green_count = max(0, green_cases - green_correct)
    overall = _rate(top1_correct, total_cases)
    green_accuracy = _rate(green_correct, green_cases)
    green_coverage = _rate(green_cases, total_cases)
    false_green_rate = _rate(wrong_green_count, green_cases)
    invalid_rate = _rate(invalid_future_years, future_years)
    score = (
        1000 * green_accuracy
        + 300 * green_coverage
        - 5000 * false_green_rate
        - 10000 * wrong_green_count
        + 100 * overall
        - 500 * invalid_rate
    )
    yellow_red_cases = max(0, total_cases - green_cases)
    yellow_red_mismatches = max(0, (mismatch_count if mismatch_count is not None else total_cases - top1_correct) - wrong_green_count)
    capture_rate = 1.0 if (mismatch_count if mismatch_count is not None else total_cases - top1_correct) == 0 else _rate(yellow_red_mismatches, yellow_red_cases)
    return {
        "objective_score": round(score, 6),
        "overall_top1_accuracy": round(overall * 100, 2),
        "green_zone_accuracy": round(green_accuracy * 100, 2),
        "green_zone_coverage": round(green_coverage * 100, 2),
        "false_green_rate": false_green_rate,
        "wrong_green_count": wrong_green_count,
        "yellow_red_capture_rate": capture_rate,
        "invalid_future_year_total_rate": invalid_rate,
        "mismatch_count": mismatch_count if mismatch_count is not None else total_cases - top1_correct,
        "claim_ready": bool(
            green_cases > 0
            and green_accuracy >= 0.99
            and green_coverage >= 0.85
            and false_green_rate <= 0.005
            and wrong_green_count == 0
            and invalid_rate == 0
        ),
    }


def objective_from_backtest(result: dict[str, Any], *, invalid_future_years: int = 0, future_years: int = 0) -> dict[str, Any]:
    return objective_from_counts(
        total_cases=int(result.get("months_tested", 0) or 0),
        top1_correct=int(result.get("exact_matches", 0) or 0),
        green_cases=int(result.get("green_zone_cases", 0) or 0),
        green_correct=int(result.get("green_zone_passed", 0) or 0),
        invalid_future_years=invalid_future_years,
        future_years=future_years,
        mismatch_count=sum(len(run.get("mismatch_details", [])) for run in result.get("runs", [])),
    )
