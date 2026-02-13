"""Observance plugin protocols."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol


@dataclass
class ObservanceRule:
    id: str
    name: str
    calendar_family: str
    method: str
    confidence: str


@dataclass
class ObservanceDate:
    rule_id: str
    start_date: date
    end_date: date
    confidence: str
    method: str


class ObservancePlugin(Protocol):
    plugin_id: str

    def list_rules(self) -> list[ObservanceRule]:
        ...

    def calculate(self, rule_id: str, year: int, mode: str = "computed") -> ObservanceDate | None:
        ...
