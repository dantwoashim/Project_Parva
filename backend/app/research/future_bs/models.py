"""Shared models and constants for future BS prediction."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from app.calendar.constants import BS_MONTH_NAMES

METHOD_VERSION = "parva_authority_aware_solar_civil_v7"
CALIBRATION_VERSION = "de440_source_stratified_authority_civil_2000_2083_v5"
MONTH_DAY_VALUES = (29, 30, 31, 32)
PREDICTION_MAX_YEAR = 2200


@dataclass(frozen=True)
class SolarIngressEvent:
    bs_month: int
    bs_month_name: str
    rashi_index: int
    rashi_name: str
    datetime_utc: datetime
    datetime_nepal: datetime
    ephemeris: str = "swiss_moshier"
    calculation_version: str = "sankranti_engine_v1"

    @property
    def nepal_date(self) -> date:
        return self.datetime_nepal.date()

    def payload(self) -> dict[str, Any]:
        return {
            "bs_month": self.bs_month,
            "bs_month_name": self.bs_month_name,
            "rashi_index": self.rashi_index,
            "rashi_name": self.rashi_name,
            "datetime_utc": self.datetime_utc.isoformat(),
            "datetime_nepal": self.datetime_nepal.isoformat(),
            "nepal_date": self.nepal_date.isoformat(),
            "ephemeris": self.ephemeris,
            "calculation_version": self.calculation_version,
        }


@dataclass(frozen=True)
class RulePrediction:
    model: str
    model_family: str
    months: list[int]
    month_starts: list[date]
    rule_weight: float
    risk_flags: list[str]
    events: list[SolarIngressEvent]
    rule_assignments: list[dict[str, Any]] | None = None

    def payload(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "model_family": self.model_family,
            "months": self.months,
            "month_starts": [value.isoformat() for value in self.month_starts],
            "year_total": sum(self.months),
            "rule_weight": round(self.rule_weight, 4),
            "risk_flags": self.risk_flags,
            "events": [event.payload() for event in self.events],
            "rule_assignments": self.rule_assignments or [],
        }


@dataclass(frozen=True)
class LegacyPrediction:
    model: str
    model_family: str
    months: list[int]
    weight: float
    model_outputs: list[dict[str, Any]]

    def payload(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "model_family": self.model_family,
            "months": self.months,
            "year_total": sum(self.months),
            "weight": round(self.weight, 4),
            "model_outputs": self.model_outputs,
        }


def month_name(month: int) -> str:
    return BS_MONTH_NAMES[month - 1]
