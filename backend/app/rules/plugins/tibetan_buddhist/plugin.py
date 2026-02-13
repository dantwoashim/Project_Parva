"""Tibetan/Buddhist observance plugin (v1)."""

from __future__ import annotations

from datetime import date

from app.calendar.calculator_v2 import calculate_festival_v2
from app.rules.plugins.base import ObservanceDate, ObservanceRule


_RULES = [
    ObservanceRule(
        id="sonam-lhosar",
        name="Sonam Lhosar",
        calendar_family="tibetan_buddhist",
        method="rule_proxy",
        confidence="computed",
    ),
    ObservanceRule(
        id="gyalpo-lhosar",
        name="Gyalpo Lhosar",
        calendar_family="tibetan_buddhist",
        method="rule_proxy",
        confidence="computed",
    ),
    ObservanceRule(
        id="tamu-lhosar",
        name="Tamu Lhosar",
        calendar_family="tibetan_buddhist",
        method="rule_proxy",
        confidence="computed",
    ),
    ObservanceRule(
        id="saga-dawa",
        name="Saga Dawa (Approx)",
        calendar_family="tibetan_buddhist",
        method="approximate",
        confidence="approximate",
    ),
]


class TibetanBuddhistObservancePlugin:
    plugin_id = "tibetan_buddhist"

    def list_rules(self) -> list[ObservanceRule]:
        return list(_RULES)

    def calculate(self, rule_id: str, year: int, mode: str = "computed") -> ObservanceDate | None:
        if rule_id == "saga-dawa":
            # v1 approximation: use Buddha Jayanti as Nepal-facing proxy marker.
            proxy = calculate_festival_v2("buddha-jayanti", year)
            if not proxy:
                return None
            return ObservanceDate(
                rule_id=rule_id,
                start_date=proxy.start_date,
                end_date=proxy.end_date,
                confidence="approximate",
                method="proxy_buddha_jayanti",
            )

        result = calculate_festival_v2(rule_id, year)
        if not result:
            return None

        return ObservanceDate(
            rule_id=rule_id,
            start_date=result.start_date,
            end_date=result.end_date,
            confidence="computed",
            method=result.method,
        )
