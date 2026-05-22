"""Market-shadow witnesses for future-BS risk analysis.

HamroPatro and static/legacy tables are treated as market-continuity signals,
not official authority. This module exposes them for disagreement analysis without
letting them affect official claim-readiness.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from .hamropatro_shadow import HAMROPATRO_MONTH_LENGTHS_PATH
from .legacy_cycle_predictor import predict_legacy_cycle

PUBLICATION_STATUS = "computed_prediction_not_official"


@lru_cache(maxsize=1)
def hamropatro_shadow_years(path: str | None = None) -> dict[int, list[int]]:
    source = Path(path) if path else HAMROPATRO_MONTH_LENGTHS_PATH
    if not source.exists():
        return {}
    payload = json.loads(source.read_text(encoding="utf-8"))
    years: dict[int, list[int]] = {}
    for row in payload.get("years", []):
        bs_year = int(row["bs_year"])
        months = [int(month["days"]) for month in row.get("months", [])]
        if len(months) == 12:
            years[bs_year] = months
    return years


def hamropatro_shadow_month(bs_year: int, bs_month: int) -> int | None:
    months = hamropatro_shadow_years().get(int(bs_year))
    if not months or not 1 <= int(bs_month) <= 12:
        return None
    return months[int(bs_month) - 1]


def legacy_static_month(bs_year: int, bs_month: int) -> int:
    return predict_legacy_cycle(int(bs_year)).months[int(bs_month) - 1]


def market_shadow_payload(bs_year: int, bs_month: int) -> dict[str, Any]:
    hamro = hamropatro_shadow_month(bs_year, bs_month)
    legacy = legacy_static_month(bs_year, bs_month)
    return {
        "publication_status": PUBLICATION_STATUS,
        "bs_year": int(bs_year),
        "bs_month": int(bs_month),
        "legacy_static_prediction": legacy,
        "hamropatro_shadow_prediction": hamro,
        "source_policy": "hamropatro_shadow_experimental",
        "official_claim_usable": False,
        "claim_boundary": "Market-shadow signals are disagreement evidence only, not official authority.",
    }


__all__ = [
    "PUBLICATION_STATUS",
    "hamropatro_shadow_month",
    "hamropatro_shadow_years",
    "legacy_static_month",
    "market_shadow_payload",
]
