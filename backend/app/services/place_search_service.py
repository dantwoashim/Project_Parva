"""Normalized place search over a remote geocoding source with cached timezone lookup."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.core.request_context import DEFAULT_TZ

from .runtime_cache import cached

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OFFLINE_GAZETTEER_PATH = PROJECT_ROOT / "data" / "places" / "nepal_major_places.json"


def _default_user_agent() -> str:
    source_url = os.getenv("PARVA_SOURCE_URL", "").strip()
    if source_url:
        return f"ProjectParva/3.0 (+{source_url})"
    return "ProjectParva/3.0 (self-hosted instance)"


_NOMINATIM_ENDPOINT = os.getenv(
    "PARVA_PLACE_SEARCH_ENDPOINT",
    "https://nominatim.openstreetmap.org/search",
).strip() or "https://nominatim.openstreetmap.org/search"
_USER_AGENT = os.getenv(
    "PARVA_PLACE_SEARCH_USER_AGENT",
    _default_user_agent(),
).strip() or _default_user_agent()
_REQUEST_TIMEOUT_SECONDS = float(os.getenv("PARVA_PLACE_SEARCH_TIMEOUT_SECONDS", "5.0"))
_ATTRIBUTION = "Search results use OpenStreetMap Nominatim data."
_ALLOW_REMOTE = os.getenv("PARVA_PLACE_SEARCH_ALLOW_REMOTE", "true").strip().lower() not in {
    "0",
    "false",
    "no",
}
_TIMEZONE_FINDER = None
_OFFLINE_GAZETTEER = None


def _load_timezone_finder():
    global _TIMEZONE_FINDER
    if _TIMEZONE_FINDER is not None:
        return _TIMEZONE_FINDER

    try:
        from timezonefinder import TimezoneFinder
    except Exception:
        _TIMEZONE_FINDER = False
        return _TIMEZONE_FINDER

    _TIMEZONE_FINDER = TimezoneFinder(in_memory=True)
    return _TIMEZONE_FINDER


def _resolve_timezone(latitude: float, longitude: float) -> tuple[str, str]:
    finder = _load_timezone_finder()
    if finder is False:
        return DEFAULT_TZ, "fallback_default_timezonefinder_missing"

    timezone_name = finder.timezone_at(lat=latitude, lng=longitude) or finder.certain_timezone_at(
        lat=latitude,
        lng=longitude,
    )
    if timezone_name:
        return timezone_name, "coordinate_lookup"
    return DEFAULT_TZ, "fallback_default_lookup_miss"


def _load_offline_gazetteer() -> list[dict[str, Any]]:
    global _OFFLINE_GAZETTEER
    if _OFFLINE_GAZETTEER is not None:
        return _OFFLINE_GAZETTEER

    if not OFFLINE_GAZETTEER_PATH.exists():
        _OFFLINE_GAZETTEER = []
        return _OFFLINE_GAZETTEER

    try:
        payload = json.loads(OFFLINE_GAZETTEER_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        _OFFLINE_GAZETTEER = []
        return _OFFLINE_GAZETTEER

    rows = payload.get("places", []) if isinstance(payload, dict) else []
    _OFFLINE_GAZETTEER = [row for row in rows if isinstance(row, dict)]
    return _OFFLINE_GAZETTEER


def _tokenize(text: str) -> list[str]:
    return [part for part in text.lower().replace(",", " ").split() if part]


def _offline_match_score(row: dict[str, Any], query: str) -> int:
    query_normalized = query.strip().lower()
    if not query_normalized:
        return -1

    haystacks = [str(row.get("label", "")).lower()]
    haystacks.extend(str(alias).lower() for alias in row.get("aliases", []) or [])

    score = -1
    query_tokens = _tokenize(query_normalized)
    for candidate in haystacks:
        if candidate == query_normalized:
            score = max(score, 100)
        elif candidate.startswith(query_normalized):
            score = max(score, 90)
        elif query_normalized in candidate:
            score = max(score, 75)
        elif query_tokens and all(token in candidate for token in query_tokens):
            score = max(score, 60)
    return score


def _search_offline_places(query: str, limit: int) -> list[dict[str, Any]]:
    matches: list[tuple[int, dict[str, Any]]] = []
    for row in _load_offline_gazetteer():
        score = _offline_match_score(row, query)
        if score < 0:
            continue
        matches.append((score, row))

    matches.sort(key=lambda item: (-item[0], item[1].get("label", "")))
    items: list[dict[str, Any]] = []
    for _score, row in matches[:limit]:
        items.append(
            {
                "label": str(row.get("label") or "Unknown place"),
                "latitude": float(f"{float(row['latitude']):.6f}"),
                "longitude": float(f"{float(row['longitude']):.6f}"),
                "timezone": str(row.get("timezone") or DEFAULT_TZ),
                "source": "offline_nepal_gazetteer",
                "timezone_source": "gazetteer",
            }
        )
    return items


def _fetch_nominatim_rows(query: str, limit: int) -> list[dict[str, Any]]:
    if not _ALLOW_REMOTE:
        raise RuntimeError(
            "Remote place search is disabled for this deployment. Configure an offline gazetteer or enable PARVA_PLACE_SEARCH_ALLOW_REMOTE."
        )
    params = urlencode(
        {
            "q": query,
            "format": "jsonv2",
            "addressdetails": 1,
            "limit": limit,
            "accept-language": "en",
        }
    )
    request = Request(
        f"{_NOMINATIM_ENDPOINT}?{params}",
        headers={
            "User-Agent": _USER_AGENT,
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=_REQUEST_TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"Place search upstream returned HTTP {exc.code}.") from exc
    except URLError as exc:
        raise RuntimeError("Place search upstream is unavailable.") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("Place search upstream returned malformed JSON.") from exc

    if not isinstance(payload, list):
        raise RuntimeError("Place search upstream returned an unexpected payload shape.")
    return payload


def _normalize_label(row: dict[str, Any]) -> str:
    display_name = str(row.get("display_name") or "").strip()
    if display_name:
        return display_name

    address = row.get("address") or {}
    parts = [
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("state")
        or address.get("county"),
        address.get("country"),
    ]
    label = ", ".join(str(part).strip() for part in parts if part)
    return label or "Unknown place"


def search_places(*, query: str, limit: int = 5) -> dict[str, Any]:
    normalized_query = query.strip()
    if len(normalized_query) < 2:
        raise ValueError("Place search query must be at least 2 characters.")
    if limit < 1 or limit > 8:
        raise ValueError("Place search limit must be between 1 and 8.")

    cache_key = f"place_search:{normalized_query.lower()}:{limit}"

    def _compute() -> dict[str, Any]:
        offline_items = _search_offline_places(normalized_query, limit)
        if offline_items:
            return {
                "query": normalized_query,
                "items": offline_items,
                "total": len(offline_items),
                "source": "offline_nepal_gazetteer",
                "source_mode": "offline_gazetteer",
                "attribution": "Curated offline Nepal gazetteer bundled with Project Parva.",
                "privacy_notice": "This search was resolved locally without sending the query to a remote geocoder.",
                "service_notice": "Offline results prioritize common Nepal locations for fast, privacy-preserving form entry.",
            }

        rows = _fetch_nominatim_rows(normalized_query, limit)
        items: list[dict[str, Any]] = []
        seen: set[tuple[str, float, float]] = set()

        for row in rows:
            try:
                latitude = float(row["lat"])
                longitude = float(row["lon"])
            except (KeyError, TypeError, ValueError):
                continue

            label = _normalize_label(row)
            dedupe_key = (label.lower(), round(latitude, 6), round(longitude, 6))
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            timezone_name, timezone_source = _resolve_timezone(latitude, longitude)
            items.append(
                {
                    "label": label,
                    "latitude": float(f"{latitude:.6f}"),
                    "longitude": float(f"{longitude:.6f}"),
                    "timezone": timezone_name,
                    "source": "openstreetmap_nominatim",
                    "timezone_source": timezone_source,
                }
            )

        return {
            "query": normalized_query,
            "items": items,
            "total": len(items),
            "source": "openstreetmap_nominatim",
            "source_mode": "remote_geocoder",
            "attribution": _ATTRIBUTION,
            "privacy_notice": "Place queries are sent to the configured geocoding provider for resolution.",
            "service_notice": "For privacy-sensitive or high-volume deployments, prefer an offline gazetteer over the public upstream service.",
        }

    return cached(cache_key, ttl_seconds=3600, compute=_compute)


__all__ = ["search_places"]
