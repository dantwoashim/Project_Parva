"""Date candidate scoring."""

from __future__ import annotations


def score_candidate(day: int, reasons: list[str]) -> int:
    return max(0, 100 - (len(reasons) * 40) - day // 10)
