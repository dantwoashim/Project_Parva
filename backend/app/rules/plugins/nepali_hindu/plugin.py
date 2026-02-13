"""Nepali Hindu observance plugin using existing V2 rule engine."""

from __future__ import annotations

from app.calendar.calculator_v2 import calculate_festival_v2, get_festival_rules_v3
from app.rules.plugins.base import ObservanceDate, ObservanceRule


class NepaliHinduObservancePlugin:
    plugin_id = "nepali_hindu"

    def list_rules(self) -> list[ObservanceRule]:
        rules = get_festival_rules_v3()
        out = []
        for rid, rule in rules.items():
            out.append(
                ObservanceRule(
                    id=rid,
                    name=rid.replace("-", " ").title(),
                    calendar_family="nepali_hindu",
                    method=rule.get("type", "unknown"),
                    confidence="computed",
                )
            )
        return out

    def calculate(self, rule_id: str, year: int, mode: str = "computed") -> ObservanceDate | None:
        result = calculate_festival_v2(rule_id, year)
        if not result:
            return None
        return ObservanceDate(
            rule_id=rule_id,
            start_date=result.start_date,
            end_date=result.end_date,
            confidence="official" if result.method == "override" else "computed",
            method=result.method,
        )
