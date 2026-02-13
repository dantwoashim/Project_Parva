"""Festival forecasting helpers (Year-3 M28 baseline)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import exp
from typing import Iterable

from app.rules import get_rule_service


@dataclass
class ForecastItem:
    festival_id: str
    year: int
    start_date: str
    end_date: str
    duration_days: int
    method: str
    horizon_years: int
    estimated_accuracy: float
    confidence_interval_days: int


def list_default_forecast_festivals() -> list[str]:
    return [
        "dashain",
        "tihar",
        "holi",
        "shivaratri",
        "buddha-jayanti",
        "janai-purnima",
        "teej",
        "indra-jatra",
    ]


def _horizon_years(target_year: int) -> int:
    return abs(target_year - date.today().year)


def _estimated_accuracy(horizon_years: int) -> float:
    """
    Confidence decay model.

    Starts near 99.5% and decays with horizon, lower-bounded to 70%.
    """
    base = 0.995
    decay = exp(-horizon_years / 18.0)
    return max(0.70, min(0.995, base * decay + 0.25))


def _confidence_interval_days(horizon_years: int) -> int:
    if horizon_years <= 2:
        return 0
    if horizon_years <= 5:
        return 1
    if horizon_years <= 12:
        return 2
    if horizon_years <= 20:
        return 3
    return 5


def forecast_festivals(target_year: int, festival_ids: Iterable[str]) -> list[ForecastItem]:
    service = get_rule_service()
    out: list[ForecastItem] = []

    for fid in festival_ids:
        result = service.calculate(fid, target_year)
        if not result:
            continue

        horizon = _horizon_years(target_year)
        out.append(
            ForecastItem(
                festival_id=fid,
                year=target_year,
                start_date=result.start_date.isoformat(),
                end_date=result.end_date.isoformat(),
                duration_days=result.duration_days,
                method=result.method,
                horizon_years=horizon,
                estimated_accuracy=round(_estimated_accuracy(horizon), 4),
                confidence_interval_days=_confidence_interval_days(horizon),
            )
        )

    return out


def build_error_curve(start_year: int, end_year: int) -> list[dict]:
    if end_year < start_year:
        start_year, end_year = end_year, start_year

    curve = []
    for year in range(start_year, end_year + 1):
        horizon = _horizon_years(year)
        curve.append(
            {
                "year": year,
                "horizon_years": horizon,
                "estimated_accuracy": round(_estimated_accuracy(horizon), 4),
                "confidence_interval_days": _confidence_interval_days(horizon),
            }
        )
    return curve
