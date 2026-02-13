"""Bikram Sambat calendar plugin."""

from __future__ import annotations

from datetime import date

from app.calendar.bikram_sambat import bs_to_gregorian, get_bs_confidence, gregorian_to_bs
from app.calendar.constants import get_bs_year_data

from ..base import CalendarDate, CalendarMetadata


class BikramSambatPlugin:
    plugin_id = "bs"

    def metadata(self) -> CalendarMetadata:
        return CalendarMetadata(
            plugin_id=self.plugin_id,
            calendar_family="bikram_sambat",
            version="v2",
            confidence="official|estimated",
            supports_reverse=True,
            notes="Official lookup range with estimator fallback.",
        )

    def convert_from_gregorian(self, value: date) -> CalendarDate:
        year, month, day = gregorian_to_bs(value)
        return CalendarDate(
            year=year,
            month=month,
            day=day,
            month_name=None,
            formatted=f"{year:04d}-{month:02d}-{day:02d}",
        )

    def convert_to_gregorian(self, year: int, month: int, day: int) -> date:
        return bs_to_gregorian(year, month, day)

    def month_lengths(self, year: int) -> list[int]:
        data = get_bs_year_data(year)
        if data:
            lengths, _ = data
            return lengths
        return [31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 29, 31]

    def validate(self, year: int, month: int, day: int) -> bool:
        if month < 1 or month > 12:
            return False
        lengths = self.month_lengths(year)
        return 1 <= day <= lengths[month - 1]

    def confidence_for_gregorian(self, value: date) -> str:
        return get_bs_confidence(value)
