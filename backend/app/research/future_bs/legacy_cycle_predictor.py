"""Legacy cycle-based month-length predictor kept as a weak ensemble model."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.calendar.constants import BS_MAX_YEAR, BS_MIN_YEAR, BS_MONTH_LENGTHS

from .models import LegacyPrediction

MAX_CALIBRATION_CYCLE = 60
DEFAULT_ENSEMBLE_SIZE = 5


def month_match_count(predicted: list[int], actual: list[int]) -> int:
    return sum(predicted_days == actual_days for predicted_days, actual_days in zip(predicted, actual))


def cycle_training_score(cycle_length: int, train_start: int, train_end: int) -> float:
    exact_matches = 0
    months_tested = 0
    for year in range(train_start + cycle_length, train_end + 1):
        previous_year = year - cycle_length
        if previous_year not in BS_MONTH_LENGTHS or year not in BS_MONTH_LENGTHS:
            continue
        exact_matches += month_match_count(BS_MONTH_LENGTHS[previous_year], BS_MONTH_LENGTHS[year])
        months_tested += 12
    return exact_matches / months_tested if months_tested else 0.0


def calibrated_cycles(
    train_start: int = BS_MIN_YEAR,
    train_end: int = BS_MAX_YEAR,
    *,
    ensemble_size: int = DEFAULT_ENSEMBLE_SIZE,
) -> list[tuple[int, float]]:
    max_cycle = min(MAX_CALIBRATION_CYCLE, max(1, train_end - train_start))
    scored = [
        (cycle, cycle_training_score(cycle, train_start, train_end))
        for cycle in range(1, max_cycle + 1)
    ]
    scored = [row for row in scored if row[1] > 0]
    scored.sort(key=lambda row: (row[1], row[0] in {4, 8, 23, 27, 31, 35}), reverse=True)
    return scored[:ensemble_size]


def corpus_cycle_pattern(bs_year: int, cycle_length: int) -> tuple[int, list[int]]:
    candidate = bs_year - cycle_length
    while candidate > BS_MAX_YEAR:
        candidate -= cycle_length
    while candidate < BS_MIN_YEAR:
        candidate += cycle_length
    if candidate not in BS_MONTH_LENGTHS:
        candidate = min(BS_MONTH_LENGTHS, key=lambda year: abs(year - candidate))
    return candidate, list(BS_MONTH_LENGTHS[candidate])


def predict_legacy_cycle(bs_year: int) -> LegacyPrediction:
    model_outputs: list[dict[str, Any]] = []
    cycles = calibrated_cycles()
    for cycle_length, score in cycles:
        source_year, months = corpus_cycle_pattern(bs_year, cycle_length)
        model_outputs.append(
            {
                "model": f"calibrated_cycle_{cycle_length}",
                "source_year": source_year,
                "training_score": round(score * 100, 2),
                "months": months,
            }
        )

    predicted: list[int] = []
    for month_index in range(12):
        weighted_votes: Counter[int] = Counter()
        for model in model_outputs:
            weighted_votes[model["months"][month_index]] += float(model["training_score"])
        predicted.append(weighted_votes.most_common(1)[0][0])

    average_weight = sum(score for _, score in cycles) / len(cycles) if cycles else 0.15
    return LegacyPrediction(
        model="legacy_cycle_model",
        model_family="legacy_static_cycle_heuristic",
        months=predicted,
        weight=average_weight * 0.65,
        model_outputs=model_outputs,
    )


def predict_from_training(
    bs_year: int,
    train_start: int,
    train_end: int,
) -> tuple[list[int], list[dict[str, Any]]]:
    cycles = calibrated_cycles(train_start, train_end, ensemble_size=3)
    model_outputs: list[dict[str, Any]] = []
    for cycle_length, score in cycles:
        source_year = bs_year - cycle_length
        if source_year < train_start or source_year > train_end:
            continue
        model_outputs.append(
            {
                "model": f"calibrated_cycle_{cycle_length}",
                "training_score": round(score * 100, 2),
                "source_year": source_year,
                "months": list(BS_MONTH_LENGTHS[source_year]),
            }
        )
    if not model_outputs:
        model_outputs.append(
            {
                "model": "training_tail_fallback",
                "training_score": 0.0,
                "source_year": train_end,
                "months": list(BS_MONTH_LENGTHS[train_end]),
            }
        )

    predicted: list[int] = []
    for month_index in range(12):
        weighted_votes: Counter[int] = Counter()
        for model in model_outputs:
            weighted_votes[model["months"][month_index]] += float(model["training_score"]) or 1.0
        predicted.append(weighted_votes.most_common(1)[0][0])
    return predicted, model_outputs
