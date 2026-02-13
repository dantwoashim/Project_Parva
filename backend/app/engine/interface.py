"""Engine protocol definitions."""

from __future__ import annotations

from datetime import date, datetime
from typing import Protocol

from .types import ConversionResult, PanchangaResult, TithiResult


class EngineInterface(Protocol):
    """Contract any calendrical computation engine must satisfy."""

    def calculate_tithi(self, dt: date | datetime) -> TithiResult:
        """Calculate tithi and metadata."""

    def calculate_panchanga(self, dt: date | datetime) -> PanchangaResult:
        """Calculate full panchanga and metadata."""

    def convert_date(self, from_calendar: str, to_calendar: str, value: str) -> ConversionResult:
        """Convert between supported calendars."""
