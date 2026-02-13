"""Festival rule service (V2-first)."""

from __future__ import annotations

from datetime import date
from typing import Any

from app.calendar.calculator_v2 import (
    calculate_festival_v2,
    get_festivals_on_date_v2,
    get_festival_info_v2,
    get_upcoming_festivals_v2,
    list_festivals_v2,
)


class FestivalRuleService:
    """Thin service wrapper over the V2 rule engine."""

    def calculate(self, festival_id: str, year: int):
        return calculate_festival_v2(festival_id, year)

    def upcoming(self, from_date: date, days: int = 30):
        return get_upcoming_festivals_v2(from_date, days=days)

    def on_date(self, target_date: date):
        return get_festivals_on_date_v2(target_date)

    def info(self, festival_id: str) -> dict[str, Any] | None:
        return get_festival_info_v2(festival_id)

    def list_ids(self) -> list[str]:
        return list_festivals_v2()


def get_rule_service() -> FestivalRuleService:
    return FestivalRuleService()
