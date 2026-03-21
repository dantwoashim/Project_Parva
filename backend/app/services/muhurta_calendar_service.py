"""Date-ranked muhurta summaries for calendar-first planning."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from app.calendar.muhurta import get_auspicious_windows

from .runtime_cache import cached


def _selected_windows(ranked: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    ranking_profile = ranked.get("ranking_profile") or {}
    minimum_score = int(ranking_profile.get("minimum_score", 0))
    ranked_rows = list(ranked.get("ranked_muhurtas") or [])
    selected = [row for row in ranked_rows if int(row.get("score", -999)) >= minimum_score]
    return selected, minimum_score


def _best_window_for_ranked(ranked: dict[str, Any]) -> tuple[dict[str, Any], bool, int]:
    ranked_rows = list(ranked.get("ranked_muhurtas") or [])
    selected, minimum_score = _selected_windows(ranked)
    if selected:
        return selected[0], True, minimum_score
    if ranked_rows:
        return ranked_rows[0], False, minimum_score
    return {}, False, minimum_score


def _tone_for_score(score: int | float | None, *, viable: bool) -> str:
    if score is None:
        return "unavailable"
    numeric = float(score)
    if viable and numeric >= 70:
        return "strong"
    if viable and numeric >= 45:
        return "good"
    if numeric <= 0:
        return "avoid"
    return "mixed"


def _summarize_day(target_date: date, ranked: dict[str, Any]) -> dict[str, Any]:
    best_window, viable, minimum_score = _best_window_for_ranked(ranked)
    score = best_window.get("score")
    return {
        "date": target_date.isoformat(),
        "type": ranked.get("ceremony_type", "general"),
        "has_viable_window": viable,
        "minimum_score": minimum_score,
        "top_score": score,
        "tone": _tone_for_score(score, viable=viable),
        "window_count": len(ranked.get("ranked_muhurtas") or []),
        "best_window": {
            "index": best_window.get("index"),
            "name": best_window.get("name"),
            "start": best_window.get("start"),
            "end": best_window.get("end"),
            "score": score,
            "quality": best_window.get("quality"),
            "reason_codes": list(best_window.get("reason_codes") or []),
            "rank_explanation": best_window.get("rank_explanation"),
        }
        if best_window
        else None,
        "caution": {
            "rahu_kalam": (ranked.get("avoid") or {}).get("rahu_kalam"),
            "yamaganda": (ranked.get("avoid") or {}).get("yamaganda"),
            "gulika": (ranked.get("avoid") or {}).get("gulika"),
        },
    }


def build_muhurta_calendar(
    *,
    from_date: date,
    to_date: date,
    latitude: float,
    longitude: float,
    timezone_name: str,
    ceremony_type: str,
    assumption_set: str,
) -> dict[str, Any]:
    if from_date > to_date:
        raise ValueError("'from' date must be <= 'to' date")

    total_days = (to_date - from_date).days + 1
    if total_days > 62:
        raise ValueError("Muhurta calendar range must not exceed 62 days.")

    cache_key = (
        f"muhurta_calendar:{from_date.isoformat()}:{to_date.isoformat()}:{latitude:.4f}:"
        f"{longitude:.4f}:{timezone_name}:{ceremony_type}:{assumption_set}"
    )

    def _compute() -> dict[str, Any]:
        days: list[dict[str, Any]] = []
        current = from_date
        while current <= to_date:
            ranked = get_auspicious_windows(
                current,
                lat=latitude,
                lon=longitude,
                ceremony_type=ceremony_type,
                tz_name=timezone_name,
                assumption_set_id=assumption_set,
            )
            days.append(_summarize_day(current, ranked))
            current += timedelta(days=1)

        return {
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "timezone": timezone_name,
            },
            "type": ceremony_type,
            "assumption_set_id": assumption_set,
            "days": days,
            "total": len(days),
        }

    return cached(cache_key, ttl_seconds=1800, compute=_compute)


__all__ = ["build_muhurta_calendar"]
