"""Compatibility bridge for the legacy festival calculator engine."""

from __future__ import annotations

from app.calendar.calculator_v2 import (
    FestivalDate,
    calculate_festival_v2,
    get_festival_info_v2,
    get_festival_rules_v3,
    get_festivals_on_date_v2,
    get_upcoming_festivals_v2,
    list_festivals_v2,
)

__all__ = [
    "FestivalDate",
    "calculate_festival_v2",
    "get_festival_info_v2",
    "get_festival_rules_v3",
    "get_festivals_on_date_v2",
    "get_upcoming_festivals_v2",
    "list_festivals_v2",
]
