"""Tibetan calendar plugin (v1 approximate mode)."""

from __future__ import annotations

from datetime import date

from ..base import CalendarDate, CalendarMetadata


TIBETAN_YEAR_OFFSET = 127
TIBETAN_MONTH_NAMES = {
    1: "First Month",
    2: "Second Month",
    3: "Third Month",
    4: "Saga Dawa Month",
    5: "Fifth Month",
    6: "Sixth Month",
    7: "Seventh Month",
    8: "Eighth Month",
    9: "Ninth Month",
    10: "Tenth Month",
    11: "Eleventh Month",
    12: "Twelfth Month",
}


class TibetanCalendarPlugin:
    plugin_id = "tibetan"

    def metadata(self) -> CalendarMetadata:
        return CalendarMetadata(
            plugin_id=self.plugin_id,
            calendar_family="tibetan",
            version="v1",
            confidence="approximate",
            supports_reverse=False,
            notes="Approximate calendar shell for observance integration; table-backed precision planned.",
        )

    def convert_from_gregorian(self, value: date) -> CalendarDate:
        # v1 approximate year mapping for plugin demonstration and API integration.
        tib_year = value.year + TIBETAN_YEAR_OFFSET
        month_name = TIBETAN_MONTH_NAMES.get(value.month)
        return CalendarDate(
            year=tib_year,
            month=value.month,
            day=value.day,
            month_name=month_name,
            formatted=f"TY {tib_year} M{value.month:02d} D{value.day:02d}",
        )

    def convert_to_gregorian(self, year: int, month: int, day: int) -> date:
        raise ValueError("Reverse Tibetan conversion not supported in v1 plugin")

    def month_lengths(self, year: int) -> list[int]:
        return [30 if i % 2 == 0 else 29 for i in range(12)]

    def validate(self, year: int, month: int, day: int) -> bool:
        if month < 1 or month > 12:
            return False
        return 1 <= day <= self.month_lengths(year)[month - 1]
