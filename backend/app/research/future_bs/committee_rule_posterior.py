"""Computed committee/civil-rule posterior for future BS model-risk."""

from __future__ import annotations

import math
from collections import Counter
from functools import lru_cache
from typing import Any, Iterable

from .accuracy import source_policy_allows
from .corpus import CorpusRow, corpus_rows

POSTERIOR_RULES = (
    "month_specific_cutoff",
    "precedent_rule",
    "same_day",
    "sunrise_rule",
    "era_specific_cutoff",
)


def _source_weight(row: CorpusRow) -> float:
    return {
        "official_verified": 1.0,
        "printed_verified": 0.92,
        "physical_patro_verified": 0.92,
        "approved_patro": 0.78,
        "institutional_reference": 0.68,
        "publisher_consensus": 0.64,
        "third_party_reference": 0.42,
        "internal_reference": 0.58,
    }.get(row.source_type, 0.0)


def _recency_weight(row_year: int, target_year: int) -> float:
    distance = max(0, target_year - row_year)
    return 0.55 + 0.45 * math.exp(-distance / 18.0)


def _month_weight(row_month: int, target_month: int) -> float:
    return 1.0 if row_month == target_month else 0.18


def _year_total_valid(row: CorpusRow) -> bool:
    return sum(row.months) in {365, 366}


def _weighted_mode(rows: Iterable[tuple[CorpusRow, float]], month: int) -> int | None:
    votes: Counter[int] = Counter()
    for row, weight in rows:
        votes[int(row.months[month - 1])] += weight
    if not votes:
        return None
    return votes.most_common(1)[0][0]


def _entropy(probabilities: dict[str, float]) -> float:
    values = [value for value in probabilities.values() if value > 0]
    if not values:
        return 0.0
    raw = -sum(value * math.log(value, 2) for value in values)
    max_entropy = math.log(len(probabilities), 2)
    return raw / max_entropy if max_entropy else 0.0


@lru_cache(maxsize=256)
def committee_rule_posterior(
    target_year: int,
    target_month: int,
    *,
    train_end: int | None = None,
    source_policy: str = "all_reference",
) -> dict[str, Any]:
    """Compute posterior weights from past source-labeled month-length behavior."""

    if target_month < 1 or target_month > 12:
        raise ValueError("target_month must be between 1 and 12.")
    effective_train_end = min(train_end if train_end is not None else target_year - 1, target_year - 1)
    training = [
        row
        for row in corpus_rows()
        if row.bs_year <= effective_train_end
        and source_policy_allows(row.source_type, row.verification_status, source_policy)
        and _year_total_valid(row)
        and _source_weight(row) > 0
    ]
    if not training:
        probabilities = {rule: round(1.0 / len(POSTERIOR_RULES), 6) for rule in POSTERIOR_RULES}
        return {
            "committee_rule_posterior": probabilities,
            "rule_entropy": 1.0,
            "method_regime_risk": "high",
            "evidence": {
                "historical_cases_used": 0,
                "source_policy": source_policy,
                "month_specific_cases": 0,
                "train_end": effective_train_end,
            },
        }

    weighted_rows = [
        (row, _source_weight(row) * _recency_weight(row.bs_year, target_year))
        for row in training
    ]
    month_rows = [
        (row, weight * _month_weight(target_month, target_month))
        for row, weight in weighted_rows
    ]
    recent_cutoff = max(min(row.bs_year for row in training), effective_train_end - 24)
    recent_rows = [(row, weight) for row, weight in weighted_rows if row.bs_year >= recent_cutoff]

    month_mode = _weighted_mode(month_rows, target_month)
    recent_mode = _weighted_mode(recent_rows, target_month) or month_mode
    all_mode = _weighted_mode(weighted_rows, target_month) or month_mode

    scores = {rule: 0.001 for rule in POSTERIOR_RULES}
    month_specific_cases = 0
    for row, base_weight in weighted_rows:
        actual = row.months[target_month - 1]
        month_case_weight = base_weight * _month_weight(target_month, target_month)
        month_specific_cases += 1
        previous_year = next((candidate for candidate in training if candidate.bs_year == row.bs_year - 1), None)
        precedent_value = (
            previous_year.months[target_month - 1]
            if previous_year is not None
            else all_mode
        )
        candidates = {
            "month_specific_cutoff": month_mode,
            "precedent_rule": precedent_value,
            "same_day": all_mode,
            "sunrise_rule": 30 if target_month in {9, 10, 11, 12} else 31,
            "era_specific_cutoff": recent_mode,
        }
        for rule, candidate in candidates.items():
            if candidate == actual:
                scores[rule] += month_case_weight
            else:
                scores[rule] += month_case_weight * 0.08

    total = sum(scores.values()) or 1.0
    probabilities = {rule: round(scores[rule] / total, 6) for rule in POSTERIOR_RULES}
    entropy = round(_entropy(probabilities), 4)
    risk = "low" if entropy < 0.45 else "medium" if entropy <= 0.72 else "high"
    return {
        "committee_rule_posterior": probabilities,
        "rule_entropy": entropy,
        "method_regime_risk": risk,
        "evidence": {
            "historical_cases_used": len(training) * 12,
            "source_policy": source_policy,
            "month_specific_cases": month_specific_cases,
            "train_end": effective_train_end,
            "recent_cutoff": recent_cutoff,
        },
    }
