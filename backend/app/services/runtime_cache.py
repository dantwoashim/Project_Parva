"""Tiny in-process TTL cache for read-heavy free-tier endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable


@dataclass
class _Entry:
    expires_at: datetime
    value: Any


_CACHE: dict[str, _Entry] = {}


def cached(key: str, ttl_seconds: int, compute: Callable[[], Any]) -> Any:
    now = datetime.now(timezone.utc)
    hit = _CACHE.get(key)
    if hit and hit.expires_at > now:
        return hit.value

    value = compute()
    _CACHE[key] = _Entry(expires_at=now + timedelta(seconds=max(1, ttl_seconds)), value=value)
    return value


def invalidate_prefix(prefix: str) -> None:
    for key in list(_CACHE.keys()):
        if key.startswith(prefix):
            _CACHE.pop(key, None)


def stats() -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    live = {k: v for k, v in _CACHE.items() if v.expires_at > now}
    return {
        "entries": len(live),
        "keys": sorted(live.keys())[:100],
    }
