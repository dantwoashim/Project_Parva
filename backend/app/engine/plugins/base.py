"""Plugin protocols for calendar engines."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol


@dataclass
class CalendarDate:
    year: int
    month: int
    day: int
    month_name: str | None = None
    formatted: str | None = None


@dataclass
class CalendarMetadata:
    plugin_id: str
    calendar_family: str
    version: str
    confidence: str
    supports_reverse: bool
    notes: str | None = None


class CalendarPlugin(Protocol):
    """Interface for calendar conversion plugins."""

    plugin_id: str

    def metadata(self) -> CalendarMetadata:
        ...

    def convert_from_gregorian(self, value: date) -> CalendarDate:
        ...

    def convert_to_gregorian(self, year: int, month: int, day: int) -> date:
        ...

    def month_lengths(self, year: int) -> list[int]:
        ...

    def validate(self, year: int, month: int, day: int) -> bool:
        ...
