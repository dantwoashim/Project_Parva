"""Chinese observance plugin (v1)."""

from __future__ import annotations

from datetime import date

from app.engine.plugins.chinese.plugin import ChineseCalendarPlugin, LUNAR_NEW_YEAR
from app.rules.plugins.base import ObservanceDate, ObservanceRule


_RULES = {
    "chinese-new-year": (1, 1),
    "dragon-boat": (5, 5),
    "mid-autumn": (8, 15),
    # Qingming is solar-term related; v1 approximation as fixed Gregorian date.
    "qingming": None,
}


class ChineseObservancePlugin:
    plugin_id = "chinese"

    def __init__(self) -> None:
        self.calendar = ChineseCalendarPlugin()

    def list_rules(self) -> list[ObservanceRule]:
        return [
            ObservanceRule(
                id=rid,
                name=rid.replace("-", " ").title(),
                calendar_family="chinese_lunisolar",
                method="approximate",
                confidence="approximate",
            )
            for rid in sorted(_RULES.keys())
        ]

    def calculate(self, rule_id: str, year: int, mode: str = "computed") -> ObservanceDate | None:
        if rule_id not in _RULES:
            return None

        if rule_id == "qingming":
            # Approximation for Nepal-facing display.
            day = 4 if year % 4 else 5
            start = date(year, 4, day)
            return ObservanceDate(
                rule_id=rule_id,
                start_date=start,
                end_date=start,
                confidence="approximate",
                method="solar_term_approx",
            )

        month_day = _RULES[rule_id]
        assert month_day is not None

        # chinese-new-year uses lunar year matching Gregorian year for festival naming.
        if rule_id == "chinese-new-year":
            if year not in LUNAR_NEW_YEAR:
                return None
            start = LUNAR_NEW_YEAR[year]
            return ObservanceDate(
                rule_id=rule_id,
                start_date=start,
                end_date=start,
                confidence="computed",
                method="lunar_new_year_table",
            )

        month, day = month_day
        # For lunar festivals, event may fall in same Gregorian year if lunar year has started.
        if year not in LUNAR_NEW_YEAR:
            return None
        try:
            start = self.calendar.convert_to_gregorian(year, month, day)
        except Exception:
            return None

        return ObservanceDate(
            rule_id=rule_id,
            start_date=start,
            end_date=start,
            confidence="approximate",
            method="lny_table_month_projection",
        )
