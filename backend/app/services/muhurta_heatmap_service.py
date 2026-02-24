"""Build 24h heatmap blocks for Muhurta UI."""

from __future__ import annotations

from datetime import date
from typing import Any

from app.calendar.muhurta import get_auspicious_windows, get_muhurtas, get_rahu_kalam

from .runtime_cache import cached


def _classify_window(row: dict[str, Any]) -> str:
    quality = row.get("quality")
    if quality == "auspicious":
        return "auspicious"
    if quality == "inauspicious":
        return "avoid"
    return "neutral"


def _reason_codes(row: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    quality = row.get("quality")
    if quality:
        reasons.append(f"quality:{quality}")

    hora = row.get("hora") or {}
    if hora.get("lord"):
        reasons.append(f"hora:{hora['lord']}")

    ch = row.get("chaughadia") or {}
    if ch.get("name"):
        reasons.append(f"chaughadia:{ch['name']}")

    if row.get("is_abhijit"):
        reasons.append("abhijit")
    if row.get("overlaps_avoidance"):
        reasons.append("overlaps_avoidance")

    return reasons


def build_muhurta_heatmap(
    *,
    target_date: date,
    latitude: float,
    longitude: float,
    timezone_name: str,
    ceremony_type: str,
    assumption_set: str,
) -> dict:
    cache_key = (
        f"muhurta_heat:{target_date.isoformat()}:{latitude:.4f}:{longitude:.4f}:"
        f"{timezone_name}:{ceremony_type}:{assumption_set}"
    )

    def _compute() -> dict:
        ranked = get_auspicious_windows(
            target_date,
            lat=latitude,
            lon=longitude,
            ceremony_type=ceremony_type,
            tz_name=timezone_name,
            assumption_set_id=assumption_set,
        )
        muhurta = get_muhurtas(
            target_date,
            lat=latitude,
            lon=longitude,
            tz_name=timezone_name,
        )
        rahu = get_rahu_kalam(target_date, lat=latitude, lon=longitude, tz_name=timezone_name)

        score_map = {int(row["index"]): int(row.get("score", 0)) for row in ranked.get("ranked_muhurtas", [])}

        blocks = []
        for row in muhurta.get("muhurtas", []):
            idx = int(row.get("index", -1))
            score = score_map.get(idx)
            blocks.append(
                {
                    "index": idx,
                    "number": row.get("number"),
                    "name": row.get("name"),
                    "period": row.get("period"),
                    "start": row.get("start"),
                    "end": row.get("end"),
                    "duration_minutes": row.get("duration_minutes"),
                    "class": _classify_window(row),
                    "score": score,
                    "reason_codes": _reason_codes(row),
                    "is_abhijit": bool(row.get("is_abhijit")),
                }
            )

        return {
            "date": target_date.isoformat(),
            "location": {"latitude": latitude, "longitude": longitude, "timezone": timezone_name},
            "type": ranked.get("ceremony_type", ceremony_type),
            "assumption_set_id": ranked.get("assumption_set_id", assumption_set),
            "best_window": ranked.get("best_window"),
            "blocks": blocks,
            "rahu_kalam": rahu.get("rahu_kalam"),
            "sunrise": muhurta.get("sunrise"),
            "sunset": muhurta.get("sunset"),
            "ranking_profile": ranked.get("ranking_profile"),
            "tara_bala": ranked.get("tara_bala"),
        }

    return cached(cache_key, ttl_seconds=180, compute=_compute)
