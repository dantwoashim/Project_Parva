"""Historical precedent tower for future BS month predictions."""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from typing import Any

from app.calendar.constants import BS_MONTH_NAMES

from .accuracy import source_policy_allows
from .corpus import CorpusRow, corpus_rows


def _source_weight(row: CorpusRow) -> float:
    return {
        "official_verified": 1.0,
        "printed_verified": 0.92,
        "physical_patro_verified": 0.92,
        "approved_patro": 0.78,
        "institutional_reference": 0.68,
        "publisher_consensus": 0.64,
        "internal_reference": 0.58,
        "third_party_reference": 0.42,
    }.get(row.source_type, 0.0)


def _similarity(row: CorpusRow, target_year: int, target_month: int) -> float:
    month_score = 1.0
    recency = max(0.0, 1.0 - min(80, target_year - row.bs_year) / 100.0)
    mod19 = 1.0 - min(abs((row.bs_year % 19) - (target_year % 19)), 9) / 9.0
    mod28 = 1.0 - min(abs((row.bs_year % 28) - (target_year % 28)), 14) / 14.0
    previous_length_score = 0.5
    if target_month > 1:
        previous = row.months[target_month - 2]
        current = row.months[target_month - 1]
        previous_length_score = 1.0 - min(abs(current - previous), 2) / 2.0
    return round(
        max(
            0.0,
            min(
                1.0,
                0.34 * month_score
                + 0.22 * recency
                + 0.16 * mod19
                + 0.12 * mod28
                + 0.16 * previous_length_score,
            ),
        ),
        6,
    )


@lru_cache(maxsize=512)
def precedent_tower(
    target_year: int,
    target_month: int,
    *,
    train_end: int | None = None,
    source_policy: str = "all_reference",
    limit: int = 5,
) -> dict[str, Any]:
    if target_month < 1 or target_month > 12:
        raise ValueError("target_month must be between 1 and 12.")
    effective_train_end = min(train_end if train_end is not None else target_year - 1, target_year - 1)
    rows = [
        row
        for row in corpus_rows()
        if row.bs_year <= effective_train_end
        and source_policy_allows(row.source_type, row.verification_status, source_policy)
        and sum(row.months) in {365, 366}
        and _source_weight(row) > 0
    ]
    scored = sorted(
        (
            (_similarity(row, target_year, target_month), row)
            for row in rows
        ),
        key=lambda item: (item[0], item[1].source_quality, item[1].bs_year),
        reverse=True,
    )
    nearest = scored[:limit]
    votes: Counter[int] = Counter()
    nearest_cases = []
    for similarity, row in nearest:
        days = int(row.months[target_month - 1])
        weight = similarity * _source_weight(row)
        votes[days] += weight
        nearest_cases.append(
            {
                "bs_year": row.bs_year,
                "month": BS_MONTH_NAMES[target_month - 1].lower(),
                "month_number": target_month,
                "official_days": days,
                "similarity": round(similarity, 4),
                "source_type": row.source_type,
                "verification_status": row.verification_status,
            }
        )
    total = sum(votes.values()) or 1.0
    probabilities = {str(days): round(votes.get(days, 0.0) / total, 6) for days in (29, 30, 31, 32)}
    confidence = max(probabilities.values()) if probabilities else 0.0
    predicted = max(probabilities, key=lambda key: probabilities[key]) if probabilities else "30"
    return {
        "predicted_days": int(predicted),
        "nearest_cases": nearest_cases,
        "precedent_probabilities": probabilities,
        "precedent_confidence": round(confidence, 6),
        "evidence": {
            "historical_cases_used": len(rows),
            "source_policy": source_policy,
            "train_end": effective_train_end,
        },
    }
