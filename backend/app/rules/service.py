"""Festival rule service (V2-first)."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from app.cache import load_precomputed_festivals_between
from app.calendar.calculator_v2 import (
    FestivalDate,
    calculate_festival_v2,
    get_festival_info_v2,
    get_festivals_on_date_v2,
    get_upcoming_festivals_v2,
    list_festivals_v2,
)


class FestivalRuleService:
    """Thin service wrapper over the V2 rule engine."""

    def calculate(self, festival_id: str, year: int):
        return calculate_festival_v2(festival_id, year)

    def upcoming(self, from_date: date, days: int = 30):
        end_date = from_date + timedelta(days=days)
        precomputed = load_precomputed_festivals_between(from_date, end_date)
        if precomputed is not None:
            results = [
                (
                    row["festival_id"],
                    FestivalDate(
                        festival_id=row["festival_id"],
                        start_date=row["start_date"],
                        end_date=row["end_date"],
                        year=row["year"],
                        method=str(row.get("method", "precomputed")),
                        lunar_month=row.get("lunar_month"),
                        is_adhik_year=bool(row.get("is_adhik_year", False)),
                    ),
                )
                for row in precomputed
            ]
            results.sort(key=lambda item: item[1].start_date)
            return results
        return get_upcoming_festivals_v2(from_date, days=days)

    def on_date(self, target_date: date):
        precomputed = load_precomputed_festivals_between(target_date, target_date)
        if precomputed is not None:
            return [
                (
                    row["festival_id"],
                    FestivalDate(
                        festival_id=row["festival_id"],
                        start_date=row["start_date"],
                        end_date=row["end_date"],
                        year=row["year"],
                        method=str(row.get("method", "precomputed")),
                        lunar_month=row.get("lunar_month"),
                        is_adhik_year=bool(row.get("is_adhik_year", False)),
                    ),
                )
                for row in precomputed
            ]
        return get_festivals_on_date_v2(target_date)

    def info(self, festival_id: str) -> dict[str, Any] | None:
        return get_festival_info_v2(festival_id)

    def list_ids(self) -> list[str]:
        return list_festivals_v2()


def get_rule_service() -> FestivalRuleService:
    return FestivalRuleService()
