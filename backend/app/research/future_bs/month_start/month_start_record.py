"""Typed month-start record for reconstructed BS corpus rows."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class MonthStartRecord:
    bs_year: int
    bs_month: int
    month_start_ad: str
    witness_count: int
    best_source_tier: int
    agreement_score: float
    verification_status: str
    manual_review_required: bool

    def payload(self) -> dict[str, object]:
        return asdict(self)
