"""Rate-limit backend abstractions and implementations."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from dataclasses import dataclass
from threading import Lock
from typing import Protocol


@dataclass(frozen=True)
class RatePolicy:
    limit: int
    window_seconds: int


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    remaining: int
    retry_after: int | None = None


class RateLimiterBackend(Protocol):
    def check(
        self,
        *,
        identifier: str,
        bucket: str,
        policy: RatePolicy,
        now: float,
    ) -> RateLimitDecision:
        """Apply the rate limit policy for a single request."""


class InMemoryRateLimiterBackend:
    """Development-friendly in-process rate limiter."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._buckets: dict[tuple[str, str], deque[float]] = defaultdict(deque)

    def check(
        self,
        *,
        identifier: str,
        bucket: str,
        policy: RatePolicy,
        now: float,
    ) -> RateLimitDecision:
        bucket_key = (bucket, identifier)
        with self._lock:
            entries = self._buckets[bucket_key]
            cutoff = now - policy.window_seconds
            while entries and entries[0] <= cutoff:
                entries.popleft()

            if len(entries) >= policy.limit:
                retry_after = max(1, int(policy.window_seconds - (now - entries[0])))
                return RateLimitDecision(allowed=False, remaining=0, retry_after=retry_after)

            entries.append(now)
            remaining = max(policy.limit - len(entries), 0)
            return RateLimitDecision(allowed=True, remaining=remaining)


class RedisRateLimiterBackend:
    """Redis-backed limiter for multi-instance deployments."""

    def __init__(self, redis_url: str) -> None:
        if not redis_url.strip():
            raise ValueError("Redis rate limiting requires PARVA_REDIS_URL.")
        self._redis_url = redis_url.strip()
        self._client = None
        self._get_client()

    def _get_client(self):
        if self._client is not None:
            return self._client

        try:
            from redis import Redis
        except ImportError as exc:  # pragma: no cover - only hit when redis backend is selected.
            raise RuntimeError(
                "Redis rate limiting requires the optional 'redis' package."
            ) from exc

        self._client = Redis.from_url(self._redis_url, decode_responses=False)
        return self._client

    def check(
        self,
        *,
        identifier: str,
        bucket: str,
        policy: RatePolicy,
        now: float,
    ) -> RateLimitDecision:
        client = self._get_client()
        key = f"parva:ratelimit:{bucket}:{identifier}"
        cutoff = now - policy.window_seconds
        member = f"{now:.6f}:{time.monotonic_ns()}".encode("utf-8")

        pipe = client.pipeline()
        pipe.zremrangebyscore(key, 0, cutoff)
        pipe.zcard(key)
        removed, current = pipe.execute()
        del removed  # Only retained for readability when debugging.

        if int(current) >= policy.limit:
            oldest = client.zrange(key, 0, 0, withscores=True)
            retry_after = policy.window_seconds
            if oldest:
                retry_after = max(1, int(policy.window_seconds - (now - float(oldest[0][1]))))
            return RateLimitDecision(allowed=False, remaining=0, retry_after=retry_after)

        pipe = client.pipeline()
        pipe.zadd(key, {member: now})
        pipe.expire(key, policy.window_seconds)
        pipe.execute()
        remaining = max(policy.limit - int(current) - 1, 0)
        return RateLimitDecision(allowed=True, remaining=remaining)


def create_rate_limiter_backend(
    *,
    backend_name: str,
    redis_url: str | None = None,
) -> RateLimiterBackend:
    normalized = (backend_name or "memory").strip().lower()
    if normalized == "memory":
        return InMemoryRateLimiterBackend()
    if normalized == "redis":
        return RedisRateLimiterBackend(redis_url or "")
    raise ValueError(
        "PARVA_RATE_LIMIT_BACKEND must be one of: memory, redis."
    )
