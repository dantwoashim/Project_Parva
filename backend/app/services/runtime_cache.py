"""Tiny in-process TTL cache for read-heavy free-tier endpoints."""

from __future__ import annotations

import os
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable


@dataclass
class _Entry:
    expires_at: datetime
    value: Any


_CACHE: "OrderedDict[str, _Entry]" = OrderedDict()
_CACHE_HITS = 0
_CACHE_MISSES = 0
_CACHE_EVICTIONS = 0
_CACHE_DISABLED = os.getenv("PARVA_RUNTIME_CACHE_ENABLED", "true").strip().lower() in {
    "0",
    "false",
    "no",
}
_MAX_ENTRIES = max(1, int(os.getenv("PARVA_RUNTIME_CACHE_MAX_ENTRIES", "128")))


def _evict_expired(now: datetime) -> None:
    expired = [key for key, entry in _CACHE.items() if entry.expires_at <= now]
    for key in expired:
        _CACHE.pop(key, None)


def clear() -> None:
    global _CACHE_HITS, _CACHE_MISSES, _CACHE_EVICTIONS
    _CACHE.clear()
    _CACHE_HITS = 0
    _CACHE_MISSES = 0
    _CACHE_EVICTIONS = 0


def cached(key: str, ttl_seconds: int, compute: Callable[[], Any]) -> Any:
    global _CACHE_HITS, _CACHE_MISSES, _CACHE_EVICTIONS
    now = datetime.now(timezone.utc)
    if _CACHE_DISABLED:
        _CACHE_MISSES += 1
        return compute()

    _evict_expired(now)
    hit = _CACHE.get(key)
    if hit and hit.expires_at > now:
        _CACHE.move_to_end(key)
        _CACHE_HITS += 1
        return hit.value

    _CACHE_MISSES += 1
    value = compute()
    _CACHE[key] = _Entry(expires_at=now + timedelta(seconds=max(1, ttl_seconds)), value=value)
    _CACHE.move_to_end(key)
    while len(_CACHE) > _MAX_ENTRIES:
        _CACHE.popitem(last=False)
        _CACHE_EVICTIONS += 1
    return value


def invalidate_prefix(prefix: str) -> None:
    for key in list(_CACHE.keys()):
        if key.startswith(prefix):
            _CACHE.pop(key, None)


def stats() -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    _evict_expired(now)
    live = {k: v for k, v in _CACHE.items() if v.expires_at > now}
    return {
        "enabled": not _CACHE_DISABLED,
        "max_entries": _MAX_ENTRIES,
        "entries": len(live),
        "hits": _CACHE_HITS,
        "misses": _CACHE_MISSES,
        "evictions": _CACHE_EVICTIONS,
        "keys": sorted(live.keys())[:100],
    }
