"""Shared ritual schema normalization helpers.

This module canonicalizes ritual data into:
    {"days": [{"name", "significance", "events": [...] }]}

It is used by festival detail and timeline APIs.
"""

from __future__ import annotations

from typing import Any


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _normalize_items(items: Any) -> list[str]:
    rows: list[str] = []
    for item in _as_list(items):
        if item is None:
            continue
        if isinstance(item, str):
            parts = [chunk.strip() for chunk in item.split(",") if chunk.strip()]
            rows.extend(parts if parts else [item.strip()])
        else:
            rows.append(str(item))
    # Preserve order while removing duplicates.
    seen: set[str] = set()
    deduped: list[str] = []
    for row in rows:
        if row not in seen:
            seen.add(row)
            deduped.append(row)
    return deduped


def _step_to_event(step: Any) -> dict[str, Any]:
    if hasattr(step, "model_dump"):
        step = step.model_dump()
    if not isinstance(step, dict):
        return {
            "title": str(step),
            "description": None,
            "time": None,
            "location": None,
            "offerings": [],
        }

    return {
        "title": step.get("name") or step.get("title") or "Ritual",
        "description": step.get("description"),
        "time": step.get("time_of_day") or step.get("time"),
        "location": step.get("location"),
        "offerings": _normalize_items(step.get("items_needed") or step.get("offerings")),
    }


def normalize_ritual_sequence(festival: Any) -> dict[str, Any] | None:
    """Normalize festival ritual data to a canonical cross-route schema."""

    if festival is None:
        return None

    daily_rituals = getattr(festival, "daily_rituals", None)
    simple_rituals = getattr(festival, "simple_rituals", None)

    if isinstance(daily_rituals, dict) and isinstance(daily_rituals.get("days"), list):
        return daily_rituals

    days: list[dict[str, Any]] = []

    if daily_rituals:
        for index, day in enumerate(_as_list(daily_rituals), start=1):
            day_obj = day.model_dump() if hasattr(day, "model_dump") else day
            if not isinstance(day_obj, dict):
                continue
            rituals = _as_list(day_obj.get("rituals"))
            days.append(
                {
                    "name": day_obj.get("name") or f"Day {day_obj.get('day') or index}",
                    "significance": day_obj.get("description") or day_obj.get("significance"),
                    "events": [_step_to_event(step) for step in rituals],
                    "is_main_day": bool(day_obj.get("is_main_day")),
                }
            )

    if not days and simple_rituals:
        days.append(
            {
                "name": getattr(festival, "name", "Festival Rituals"),
                "significance": "Primary observance sequence",
                "events": [_step_to_event(step) for step in _as_list(simple_rituals)],
                "is_main_day": True,
            }
        )

    if not days:
        return None

    return {
        "days": days,
        "total_days": len(days),
        "source": "daily_rituals" if daily_rituals else "simple_rituals",
    }


def ritual_preview(festival: Any, *, max_days: int = 1, max_events: int = 3) -> dict[str, Any] | None:
    """Return a compact ritual preview for timeline/list endpoints."""

    sequence = normalize_ritual_sequence(festival)
    if not sequence:
        return None

    preview_days = []
    for day in sequence["days"][:max_days]:
        preview_days.append(
            {
                "name": day.get("name"),
                "significance": day.get("significance"),
                "events": day.get("events", [])[:max_events],
            }
        )

    return {
        "days": preview_days,
        "source": sequence.get("source"),
    }
