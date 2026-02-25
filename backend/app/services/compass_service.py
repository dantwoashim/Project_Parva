"""Temporal Compass aggregation service."""

from __future__ import annotations

from datetime import date

from app.calendar.bikram_sambat import get_bs_month_name, gregorian_to_bs
from app.calendar.panchanga import get_panchanga
from app.calendar.muhurta import get_auspicious_windows, get_rahu_kalam
from app.festivals.repository import get_repository
from app.rules import get_rule_service
from app.rules.catalog_v4 import rule_quality_band, get_rule_v4

from .runtime_cache import cached


def _window_class(score: int | float | None) -> str:
    if score is None:
        return "neutral"
    if score >= 70:
        return "auspicious"
    if score >= 45:
        return "neutral"
    return "avoid"


def _bs_struct(g_date: date) -> dict:
    bs_year, bs_month, bs_day = gregorian_to_bs(g_date)
    month_name = get_bs_month_name(bs_month)
    return {
        "year": bs_year,
        "month": bs_month,
        "day": bs_day,
        "month_name": month_name,
        "formatted": f"{bs_year} {month_name} {bs_day}",
    }


def build_temporal_compass(
    *,
    target_date: date,
    latitude: float,
    longitude: float,
    timezone_name: str,
    quality_band: str = "computed",
) -> dict:
    cache_key = (
        f"compass:{target_date.isoformat()}:{latitude:.4f}:{longitude:.4f}:"
        f"{timezone_name}:{quality_band}"
    )

    def _compute() -> dict:
        repo = get_repository()
        rule_service = get_rule_service()

        panchanga = get_panchanga(target_date, latitude=latitude, longitude=longitude)
        bs_year, bs_month, bs_day = gregorian_to_bs(target_date)

        muhurta = get_auspicious_windows(
            target_date,
            lat=latitude,
            lon=longitude,
            ceremony_type="general",
            tz_name=timezone_name,
            birth_nakshatra=None,
            assumption_set_id="np-mainstream-v2",
        )
        rahu = get_rahu_kalam(target_date, lat=latitude, lon=longitude, tz_name=timezone_name)

        upcoming = rule_service.upcoming(target_date, days=1)
        festivals_today: list[dict] = []
        for festival_id, dates in upcoming:
            if not (dates.start_date <= target_date <= dates.end_date):
                continue
            festival = repo.get_by_id(festival_id)
            if not festival:
                continue

            rule = get_rule_v4(festival_id)
            resolved_quality = rule_quality_band(rule) if rule else "inventory"
            if quality_band != "all" and resolved_quality != quality_band:
                continue

            festivals_today.append(
                {
                    "id": festival.id,
                    "name": festival.name,
                    "name_nepali": festival.name_nepali,
                    "category": festival.category,
                    "start_date": dates.start_date.isoformat(),
                    "end_date": dates.end_date.isoformat(),
                    "bs_start": _bs_struct(dates.start_date),
                    "bs_end": _bs_struct(dates.end_date),
                    "quality_band": resolved_quality,
                    "rule_status": getattr(rule, "status", "inventory"),
                }
            )

        best_window = muhurta.get("best_window") or {}
        tithi_obj = panchanga.get("tithi", {})

        return {
            "date": target_date.isoformat(),
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "timezone": timezone_name,
            },
            "bikram_sambat": {
                "year": bs_year,
                "month": bs_month,
                "day": bs_day,
                "month_name": get_bs_month_name(bs_month),
            },
            "primary_readout": {
                "tithi_name": tithi_obj.get("name"),
                "tithi_number": tithi_obj.get("display_number"),
                "paksha": tithi_obj.get("paksha"),
                "phase_progress": round(float(tithi_obj.get("progress", 0.0) or 0.0), 2),
                "phase_ratio": round((float(tithi_obj.get("number", 1)) - 1) / 30.0, 4),
            },
            "orbital": {
                "tithi": tithi_obj.get("display_number"),
                "progress": round(float(tithi_obj.get("progress", 0.0) or 0.0), 2),
                "phase_ratio": round((float(tithi_obj.get("number", 1)) - 1) / 30.0, 4),
            },
            "horizon": {
                "sunrise": panchanga.get("sunrise"),
                "sunset": panchanga.get("sunset"),
                "current_muhurta": {
                    "name": best_window.get("name"),
                    "start": best_window.get("start"),
                    "end": best_window.get("end"),
                    "score": best_window.get("score"),
                    "class": _window_class(best_window.get("score")),
                },
                "rahu_kalam": rahu.get("rahu_kalam"),
            },
            "today": {
                "festivals": festivals_today,
                "count": len(festivals_today),
            },
            "signals": {
                "nakshatra": panchanga.get("nakshatra"),
                "yoga": panchanga.get("yoga"),
                "karana": panchanga.get("karana"),
                "vaara": panchanga.get("vaara"),
            },
            "quality_band_filter": quality_band,
            "engine": {
                "method": "ephemeris_udaya",
                "method_profile": "temporal_compass_v1",
                "ephemeris_mode": panchanga.get("mode", "swiss_moshier"),
            },
        }

    return cached(cache_key, ttl_seconds=180, compute=_compute)
