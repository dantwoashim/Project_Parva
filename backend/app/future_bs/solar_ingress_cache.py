"""Precomputed solar-ingress event cache for fast future-BS computation."""

from __future__ import annotations

import json
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

from .models import SolarIngressEvent

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ASTRONOMY_DIR = PROJECT_ROOT / "data" / "future_bs" / "astronomy"
PRIVATE_EVENTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "future_bs"
    / "private"
    / "astronomy"
    / "solar_ingress_events_1900_2200.json"
)
LEGACY_EVENTS_PATH = ASTRONOMY_DIR / "solar_ingress_events_1900_2200.json"
DEFAULT_EVENTS_PATH = PRIVATE_EVENTS_PATH if PRIVATE_EVENTS_PATH.exists() else LEGACY_EVENTS_PATH


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _event_from_payload(payload: dict[str, Any]) -> SolarIngressEvent:
    return SolarIngressEvent(
        bs_month=int(payload["bs_month"]),
        bs_month_name=str(payload["bs_month_name"]),
        rashi_index=int(payload["rashi_index"]),
        rashi_name=str(payload["rashi_name"]),
        datetime_utc=_parse_dt(str(payload["datetime_utc"])),
        datetime_nepal=_parse_dt(str(payload["datetime_nepal"])),
        ephemeris=str(payload.get("ephemeris", "unknown")),
        calculation_version=str(payload.get("calculation_version", "precomputed_solar_ingress_cache")),
    )


@lru_cache(maxsize=1)
def load_solar_ingress_cache(path: Path | None = None) -> dict[str, Any]:
    path = path or DEFAULT_EVENTS_PATH
    if not path.exists():
        return {"available": False, "years": {}, "path": str(path.relative_to(PROJECT_ROOT))}
    payload = json.loads(path.read_text(encoding="utf-8"))
    years = {
        int(year): tuple(_event_from_payload(event) for event in events)
        for year, events in payload.get("years", {}).items()
    }
    return {
        **payload,
        "available": True,
        "years": years,
        "path": str(path.relative_to(PROJECT_ROOT)),
        "trusted_precomputed_jpl_cache": payload.get("ephemeris") == "jpl_de440",
    }


def cached_events_for_gregorian_year(
    gregorian_year: int,
    *,
    ephemeris_label: str,
) -> tuple[SolarIngressEvent, ...] | None:
    payload = load_solar_ingress_cache(None)
    if not payload.get("available"):
        return None
    cache_ephemeris = payload.get("ephemeris")
    trusted_jpl_readonly = cache_ephemeris == "jpl_de440" and ephemeris_label == "swiss_moshier"
    if cache_ephemeris != ephemeris_label and not trusted_jpl_readonly:
        return None
    events = payload.get("years", {}).get(gregorian_year)
    return events if events else None


def solar_ingress_cache_status() -> dict[str, Any]:
    payload = load_solar_ingress_cache()
    years = sorted(payload.get("years", {}))
    return {
        "available": bool(payload.get("available")),
        "path": payload.get("path", str(DEFAULT_EVENTS_PATH.relative_to(PROJECT_ROOT))),
        "ephemeris": payload.get("ephemeris"),
        "year_count": len(years),
        "range": f"{years[0]}-{years[-1]} AD" if years else None,
        "generated_at": payload.get("generated_at"),
        "calculation_version": payload.get("calculation_version"),
        "trusted_precomputed_jpl_cache": bool(payload.get("trusted_precomputed_jpl_cache")),
        "served_from_trusted_precomputed_jpl_cache": bool(payload.get("trusted_precomputed_jpl_cache")),
    }
