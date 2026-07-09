"""Probability helpers for future BS ensemble votes."""

from __future__ import annotations

from collections import Counter

from .models import MONTH_DAY_VALUES


def weighted_probability(votes: list[tuple[int, float]]) -> dict[str, float]:
    counts: Counter[int] = Counter()
    total = sum(weight for _, weight in votes) or 1.0
    for days, weight in votes:
        counts[days] += weight
    return {
        f"{days}_days": round(float(counts.get(days, 0.0)) / total, 4)
        for days in MONTH_DAY_VALUES
    }


def winning_days(probability: dict[str, float]) -> int:
    return max(MONTH_DAY_VALUES, key=lambda days: probability.get(f"{days}_days", 0.0))
