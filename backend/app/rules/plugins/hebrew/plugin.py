"""Hebrew observance plugin."""

from __future__ import annotations

from datetime import date

from app.engine.plugins.hebrew.plugin import HebrewCalendarPlugin
from app.rules.plugins.base import ObservanceDate, ObservanceRule


# Hebrew month indices in this plugin:
# 7=Tishrei, 1=Nisan, 9=Kislev
_RULES: dict[str, tuple[int, int]] = {
    "rosh-hashanah": (7, 1),
    "yom-kippur": (7, 10),
    "passover": (1, 15),
    "hanukkah": (9, 25),
}


class HebrewObservancePlugin:
    plugin_id = "hebrew"

    def __init__(self) -> None:
        self.calendar = HebrewCalendarPlugin()

    def list_rules(self) -> list[ObservanceRule]:
        return [
            ObservanceRule(
                id=rid,
                name=rid.replace("-", " ").title(),
                calendar_family="hebrew",
                method="formulaic",
                confidence="computed",
            )
            for rid in sorted(_RULES)
        ]

    def _candidate_dates(self, rule_id: str, year: int) -> list[date]:
        month, day = _RULES[rule_id]
        # Gregorian year roughly = Hebrew year - 3760
        hy_guess = year + 3760
        candidates: list[date] = []
        for hy in (hy_guess - 1, hy_guess, hy_guess + 1):
            try:
                g = self.calendar.convert_to_gregorian(hy, month, day)
                if g.year == year:
                    candidates.append(g)
            except Exception:
                continue
        return sorted(set(candidates))

    def calculate(self, rule_id: str, year: int, mode: str = "computed") -> ObservanceDate | None:
        if rule_id not in _RULES:
            return None

        candidates = self._candidate_dates(rule_id, year)
        if not candidates:
            return None

        start = candidates[0]
        return ObservanceDate(
            rule_id=rule_id,
            start_date=start,
            end_date=start,
            confidence="computed",
            method="formulaic",
        )
