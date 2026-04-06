"""Normalized place search over a remote geocoding source with cached timezone lookup."""

from __future__ import annotations

import json
import os
import random
import time
from dataclasses import dataclass
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
_TIME_BUDGET_SECONDS = float(os.getenv("PARVA_PLACE_SEARCH_TIME_BUDGET_SECONDS", "8.0"))
_RETRY_ATTEMPTS = max(1, int(os.getenv("PARVA_PLACE_SEARCH_RETRY_ATTEMPTS", "2")))
_RETRY_BACKOFF_SECONDS = max(0.0, float(os.getenv("PARVA_PLACE_SEARCH_RETRY_BACKOFF_SECONDS", "0.3")))
_CACHE_TTL_SECONDS = max(30, int(os.getenv("PARVA_PLACE_SEARCH_CACHE_TTL_SECONDS", "3600")))
_ATTRIBUTION = "Search results use OpenStreetMap Nominatim data."
_ALLOW_REMOTE = os.getenv("PARVA_PLACE_SEARCH_ALLOW_REMOTE", "true").strip().lower() not in {
    "0",
    "false",
    "no",
}
_PROVIDER_CHAIN = tuple(
    part.strip().lower()
    for part in os.getenv("PARVA_PLACE_SEARCH_PROVIDER_CHAIN", "offline,nominatim").split(",")
    if part.strip()
) or ("offline", "nominatim")
_TIMEZONE_FINDER = None
_OFFLINE_GAZETTEER = None
_RETRYABLE_HTTP_CODES = {408, 425, 429, 500, 502, 503, 504}


@dataclass(frozen=True)
class PlaceProviderSpec:
    key: str
    source_mode: str
    remote: bool = False


OFFLINE_PROVIDER = PlaceProviderSpec("offline_nepal_gazetteer", "offline_gazetteer", remote=False)
NOMINATIM_PROVIDER = PlaceProviderSpec("openstreetmap_nominatim", "remote_geocoder", remote=True)


def _provider_specs() -> tuple[PlaceProviderSpec, ...]:
    mapping = {
        "offline": OFFLINE_PROVIDER,
        "offline_nepal_gazetteer": OFFLINE_PROVIDER,
        "nominatim": NOMINATIM_PROVIDER,
        "openstreetmap_nominatim": NOMINATIM_PROVIDER,
    }
    specs: list[PlaceProviderSpec] = []
    for key in _PROVIDER_CHAIN:
        spec = mapping.get(key)
        if spec and spec not in specs:
            specs.append(spec)
    return tuple(specs or (OFFLINE_PROVIDER, NOMINATIM_PROVIDER))


def _load_timezone_finder():
    global _TIMEZONE_FINDER
    if _TIMEZONE_FINDER is not None:
        return _TIMEZONE_FINDER

    try:
        from timezonefinder import TimezoneFinder
    except ImportError:
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
    started = time.monotonic()
    last_error: RuntimeError | None = None
    for attempt in range(1, _RETRY_ATTEMPTS + 1):
        remaining_budget = _TIME_BUDGET_SECONDS - (time.monotonic() - started)
        if remaining_budget <= 0:
            break
        try:
            with urlopen(request, timeout=min(_REQUEST_TIMEOUT_SECONDS, remaining_budget)) as response:
                payload = json.loads(response.read().decode("utf-8"))
            break
        except HTTPError as exc:
            last_error = RuntimeError(f"Place search upstream returned HTTP {exc.code}.")
            if exc.code not in _RETRYABLE_HTTP_CODES or attempt >= _RETRY_ATTEMPTS:
                raise last_error from exc
        except URLError as exc:
            last_error = RuntimeError("Place search upstream is unavailable.")
            if attempt >= _RETRY_ATTEMPTS:
                raise last_error from exc
        except json.JSONDecodeError as exc:
            raise RuntimeError("Place search upstream returned malformed JSON.") from exc

        jitter = random.uniform(0.0, min(0.25, _RETRY_BACKOFF_SECONDS))
        time.sleep((_RETRY_BACKOFF_SECONDS * attempt) + jitter)
    else:
        payload = None

    if payload is None:
        raise last_error or RuntimeError("Place search upstream timed out.")

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
        provider_health: list[dict[str, str]] = []
        provider_attempts: dict[str, int] = {}

        for provider in _provider_specs():
            provider_attempts[provider.key] = provider_attempts.get(provider.key, 0) + 1

            if provider is OFFLINE_PROVIDER:
                offline_items = _search_offline_places(normalized_query, limit)
                if offline_items:
                    provider_health.append({"provider": provider.key, "status": "hit"})
                    return {
                        "query": normalized_query,
                        "items": offline_items,
                        "total": len(offline_items),
                        "source": provider.key,
                        "source_mode": provider.source_mode,
                        "attribution": "Curated offline Nepal gazetteer bundled with Project Parva.",
                        "privacy_notice": "This search was resolved locally without sending the query to a remote geocoder.",
                        "service_notice": "Offline results prioritize common Nepal locations for fast, privacy-preserving form entry.",
                        "provider_chain": [spec.key for spec in _provider_specs()],
                        "provider_attempts": provider_attempts,
                        "provider_health": provider_health,
                        "cache_ttl_seconds": _CACHE_TTL_SECONDS,
                    }
                provider_health.append({"provider": provider.key, "status": "miss"})
                continue

            try:
                rows = _fetch_nominatim_rows(normalized_query, limit)
            except RuntimeError as exc:
                provider_health.append(
                    {
                        "provider": provider.key,
                        "status": "error",
                        "detail": str(exc),
                    }
                )
                continue

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
                        "source": provider.key,
                        "timezone_source": timezone_source,
                    }
                )

            provider_health.append({"provider": provider.key, "status": "hit"})
            return {
                "query": normalized_query,
                "items": items,
                "total": len(items),
                "source": provider.key,
                "source_mode": provider.source_mode,
                "attribution": _ATTRIBUTION,
                "privacy_notice": "Place queries are sent to the configured geocoding provider for resolution.",
                "service_notice": "For privacy-sensitive or high-volume deployments, prefer an offline gazetteer over the public upstream service.",
                "provider_chain": [spec.key for spec in _provider_specs()],
                "provider_attempts": provider_attempts,
                "provider_health": provider_health,
                "cache_ttl_seconds": _CACHE_TTL_SECONDS,
            }

        if any(entry["status"] == "error" for entry in provider_health):
            last_error = next(
                (entry["detail"] for entry in reversed(provider_health) if entry["status"] == "error"),
                "Place search upstream is unavailable.",
            )
            raise RuntimeError(last_error)

        raise RuntimeError("No configured place provider could resolve the query.")

    return cached(cache_key, ttl_seconds=_CACHE_TTL_SECONDS, compute=_compute)


__all__ = ["search_places"]
