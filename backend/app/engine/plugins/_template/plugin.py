"""Template calendar plugin.

Copy this folder and implement all required methods.
"""

from __future__ import annotations

from datetime import date

from app.engine.plugins.base import CalendarDate, CalendarMetadata


class TemplateCalendarPlugin:
    plugin_id = "template"

    def metadata(self) -> CalendarMetadata:
        return CalendarMetadata(
            plugin_id=self.plugin_id,
            calendar_family="template",
            version="v1",
            confidence="computed",
            supports_reverse=False,
            notes="Replace with real plugin metadata.",
        )

    def convert_from_gregorian(self, value: date) -> CalendarDate:
        raise NotImplementedError

    def convert_to_gregorian(self, year: int, month: int, day: int) -> date:
        raise NotImplementedError

    def month_lengths(self, year: int) -> list[int]:
        raise NotImplementedError

    def validate(self, year: int, month: int, day: int) -> bool:
        raise NotImplementedError
