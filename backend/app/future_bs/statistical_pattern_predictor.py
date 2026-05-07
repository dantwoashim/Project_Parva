"""Past-only statistical pattern models for BS month-length prediction.

These models never read future target rows. They use source-labeled historical
month lengths as calibration evidence and act as residual checks around the
solar-ingress civil decision model.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from typing import Any

from app.calendar.constants import BS_MIN_YEAR

from .accuracy import source_policy_allows
from .corpus import corpus_rows
from .models import MONTH_DAY_VALUES
from .solar_ingress_predictor import DEFAULT_REFERENCE_TRAIN_END, predict_solar_ingress_year

DEFAULT_PATTERN_SOURCE_POLICY = "all_reference"
ANALOG_LOOKBACK_YEARS = 10
MODERN_SOLAR_OVERRIDE_START = 2078
MODERN_SOLAR_OVERRIDE_MONTHS = {3, 4, 5, 6}
GREEN_STABLE_ANALOG_MONTHS: set[int] = set()


def _month_match_count(left: list[int], right: list[int]) -> int:
    return sum(a == b for a, b in zip(left, right))


@lru_cache(maxsize=256)
def _training_data(
    train_start: int,
    train_end: int,
    source_policy: str,
) -> tuple[tuple[int, tuple[int, ...]], ...]:
    rows = []
    for row in corpus_rows():
        if not train_start <= row.bs_year <= train_end:
            continue
        if not source_policy_allows(row.source_type, row.verification_status, source_policy):
            continue
        if sum(row.months) not in {365, 366}:
            continue
        rows.append((row.bs_year, tuple(row.months)))
    return tuple(sorted(rows))


def _data_dict(
    train_start: int,
    train_end: int,
    source_policy: str,
) -> dict[int, list[int]]:
    return {
        year: list(months)
        for year, months in _training_data(train_start, train_end, source_policy)
    }


def _cycle_training_score(
    cycle_length: int,
    data: dict[int, list[int]],
) -> float:
    exact_matches = 0
    months_tested = 0
    for year in sorted(data):
        previous_year = year - cycle_length
        if previous_year not in data:
            continue
        exact_matches += _month_match_count(data[previous_year], data[year])
        months_tested += 12
    return exact_matches / months_tested if months_tested else 0.0


def _source_for_cycle(
    bs_year: int,
    cycle_length: int,
    data: dict[int, list[int]],
) -> int | None:
    if not data:
        return None
    min_year = min(data)
    max_year = max(data)
    candidate = bs_year - cycle_length
    while candidate > max_year:
        candidate -= cycle_length
    while candidate < min_year:
        candidate += cycle_length
    return candidate if candidate in data else None


def _cycle_ensemble_prediction(
    bs_year: int,
    data: dict[int, list[int]],
    *,
    ensemble_size: int = 3,
) -> dict[str, Any] | None:
    if not data:
        return None
    max_cycle = min(60, max(1, max(data) - min(data)))
    scored = [
        (cycle, _cycle_training_score(cycle, data))
        for cycle in range(1, max_cycle + 1)
    ]
    scored = [row for row in scored if row[1] > 0]
    scored.sort(key=lambda row: (row[1], row[0] in {4, 8, 23, 27, 31, 35}), reverse=True)

    model_outputs: list[dict[str, Any]] = []
    for cycle_length, score in scored[:ensemble_size]:
        source_year = _source_for_cycle(bs_year, cycle_length, data)
        if source_year is None:
            continue
        model_outputs.append(
            {
                "model": f"past_cycle_{cycle_length}",
                "source_year": source_year,
                "training_score": round(score * 100, 2),
                "months": data[source_year],
            }
        )
    if not model_outputs:
        fallback_year = max(data)
        model_outputs.append(
            {
                "model": "training_tail_fallback",
                "source_year": fallback_year,
                "training_score": 0.0,
                "months": data[fallback_year],
            }
        )

    months: list[int] = []
    for month_index in range(12):
        votes: Counter[int] = Counter()
        for output in model_outputs:
            weight = float(output["training_score"]) or 1.0
            votes[int(output["months"][month_index])] += weight
        months.append(votes.most_common(1)[0][0])

    return {
        "model": "statistical_cycle_ensemble",
        "model_family": "past_only_statistical_pattern",
        "months": months,
        "model_outputs": model_outputs,
    }


def _analog_pattern_prediction(
    bs_year: int,
    data: dict[int, list[int]],
    *,
    lookback_years: int = ANALOG_LOOKBACK_YEARS,
) -> dict[str, Any] | None:
    context_years = range(bs_year - lookback_years, bs_year)
    if any(year not in data for year in context_years):
        return None

    target_context = [
        days
        for year in context_years
        for days in data[year]
    ]
    candidates: list[tuple[int, int]] = []
    for source_year in sorted(data):
        if source_year >= bs_year:
            continue
        source_context_years = range(source_year - lookback_years, source_year)
        if any(year not in data for year in source_context_years):
            continue
        source_context = [
            days
            for year in source_context_years
            for days in data[year]
        ]
        score = _month_match_count(target_context, source_context)
        candidates.append((score, source_year))

    if not candidates:
        return None
    candidates.sort(key=lambda row: (row[0], row[1]), reverse=True)
    best_score, source_year = candidates[0]
    second_score = candidates[1][0] if len(candidates) > 1 else 0
    return {
        "model": f"statistical_analog_{lookback_years}_year",
        "model_family": "past_only_statistical_pattern",
        "months": data[source_year],
        "source_year": source_year,
        "analog_score": best_score,
        "analog_score_gap": best_score - second_score,
        "model_outputs": [
            {
                "model": f"nearest_{lookback_years}_year_history",
                "source_year": source_year,
                "training_score": round(best_score / (lookback_years * 12) * 100, 2),
                "score_gap": best_score - second_score,
                "months": data[source_year],
            }
        ],
    }


def predict_statistical_patterns(
    bs_year: int,
    *,
    train_start: int = BS_MIN_YEAR,
    train_end: int = DEFAULT_REFERENCE_TRAIN_END,
    source_policy: str = DEFAULT_PATTERN_SOURCE_POLICY,
) -> dict[str, Any] | None:
    """Predict from historical month-length patterns only."""

    data = _data_dict(train_start, train_end, source_policy)
    if not data:
        return None

    analog = _analog_pattern_prediction(bs_year, data)
    cycle = _cycle_ensemble_prediction(bs_year, data)
    primary = analog or cycle
    if primary is None:
        return None

    outputs = []
    if analog is not None:
        outputs.append(analog)
    if cycle is not None:
        outputs.append(cycle)

    return {
        "model": "past_only_statistical_pattern_stack",
        "model_family": "past_only_statistical_pattern",
        "primary_model": primary["model"],
        "months": list(primary["months"]),
        "year_total": sum(primary["months"]),
        "model_outputs": outputs,
    }


def _probability(
    *,
    final_days: int,
    base_days: int,
    solar_days: int,
    final_source: str,
) -> dict[str, float]:
    votes: Counter[int] = Counter()
    if final_source == "solar_modern_override":
        votes[solar_days] += 0.72
        votes[base_days] += 0.28
    elif final_source == "statistical_pattern":
        votes[base_days] += 0.72
        votes[solar_days] += 0.28
    else:
        votes[final_days] += 1.0
    total = sum(votes.values()) or 1.0
    return {
        f"{days}_days": round(votes.get(days, 0.0) / total, 4)
        for days in MONTH_DAY_VALUES
    }


def predict_stacked_year(
    bs_year: int,
    *,
    train_start: int = BS_MIN_YEAR,
    train_end: int = DEFAULT_REFERENCE_TRAIN_END,
    source_policy: str = DEFAULT_PATTERN_SOURCE_POLICY,
) -> dict[str, Any]:
    """Predict using solar ingress plus past-only residual pattern checks."""

    solar = predict_solar_ingress_year(bs_year, train_start=train_start, train_end=train_end)
    statistical = predict_statistical_patterns(
        bs_year,
        train_start=train_start,
        train_end=train_end,
        source_policy=source_policy,
    )
    base_months = list(statistical["months"]) if statistical else list(solar["months"])
    disagreement_count = sum(
        base_days != solar_days
        for base_days, solar_days in zip(base_months, solar["months"])
    )

    final_months: list[int] = []
    details: list[dict[str, Any]] = []
    for index, (base_days, solar_days) in enumerate(zip(base_months, solar["months"]), start=1):
        final_days = base_days
        final_source = "statistical_pattern" if statistical else "solar_ingress"
        risk_flags: list[str] = []

        if (
            statistical
            and bs_year >= MODERN_SOLAR_OVERRIDE_START
            and index in MODERN_SOLAR_OVERRIDE_MONTHS
            and base_days != solar_days
        ):
            final_days = solar_days
            final_source = "solar_modern_override"
            risk_flags.append("modern_solar_civil_override")
        elif statistical and base_days != solar_days:
            risk_flags.append("resolved_statistical_solar_disagreement")

        green_stable_disagreement = (
            statistical
            and base_days != solar_days
            and index in GREEN_STABLE_ANALOG_MONTHS
            and final_source == "statistical_pattern"
        )
        green_modern_override = final_source == "solar_modern_override"
        green_agreement = base_days == solar_days and disagreement_count <= 4

        if green_agreement or green_stable_disagreement or green_modern_override:
            confidence_score = 0.992
            risk_label = "GREEN"
        else:
            confidence_score = 0.82 if base_days == solar_days else 0.74
            risk_label = "YELLOW"
            risk_flags.append("manual_review_recommended")
            if base_days != solar_days:
                risk_flags.append("model_disagreement")

        if disagreement_count >= 4:
            risk_flags.append("year_level_model_disagreement")

        probability = _probability(
            final_days=final_days,
            base_days=base_days,
            solar_days=solar_days,
            final_source=final_source,
        )
        final_months.append(final_days)
        details.append(
            {
                "month": index,
                "final_days": final_days,
                "solar_days": solar_days,
                "statistical_days": base_days if statistical else None,
                "final_source": final_source,
                "probability": probability,
                "confidence_score": confidence_score,
                "risk_label": risk_label,
                "risk_flags": sorted(set(risk_flags)),
                "model_agreement": "2/2" if base_days == solar_days else "1/2",
            }
        )

    all_risk_flags = sorted({flag for detail in details for flag in detail["risk_flags"]})
    return {
        "model": "solar_statistical_stack_v1",
        "model_family": "computational_solar_ingress",
        "model_subfamily": "solar_civil_plus_past_pattern_stack",
        "months": final_months,
        "year_total": sum(final_months),
        "month_details": details,
        "risk_flags": all_risk_flags,
        "solar": solar,
        "statistical": statistical,
        "source_policy": source_policy,
        "disagreement_count": disagreement_count,
        "note": (
            "Stacked prediction uses solar ingress plus historical pattern calibration; "
            "historical rows are calibration evidence, not future lookup output."
        ),
    }
