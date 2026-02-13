"""Nepal Sambat plugin (approximate conversion model)."""

from __future__ import annotations

from datetime import date

from app.calendar.nepal_sambat import format_ns_date, get_current_ns_year

from ..base import CalendarDate, CalendarMetadata


class NepalSambatPlugin:
    plugin_id = "ns"

    def metadata(self) -> CalendarMetadata:
        return CalendarMetadata(
            plugin_id=self.plugin_id,
            calendar_family="nepal_sambat",
            version="v1",
            confidence="approximate",
            supports_reverse=False,
            notes="Forward conversion uses current NS year model; reverse conversion is not canonical.",
        )

    def convert_from_gregorian(self, value: date) -> CalendarDate:
        ns_year = get_current_ns_year(value)
        return CalendarDate(
            year=ns_year,
            month=value.month,
            day=value.day,
            month_name=None,
            formatted=format_ns_date(value),
        )

    def convert_to_gregorian(self, year: int, month: int, day: int) -> date:
        raise ValueError("Reverse Nepal Sambat conversion not supported in v1 plugin")

    def month_lengths(self, year: int) -> list[int]:
        # Approximate alternating lunar month lengths.
        return [30 if i % 2 == 0 else 29 for i in range(12)]

    def validate(self, year: int, month: int, day: int) -> bool:
        if month < 1 or month > 12:
            return False
        return 1 <= day <= self.month_lengths(year)[month - 1]
