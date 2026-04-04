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

    _ATOMIC_CHECK_SCRIPT = """
local key = KEYS[1]
local cutoff = tonumber(ARGV[1])
local limit = tonumber(ARGV[2])
local now_score = tonumber(ARGV[3])
local member = ARGV[4]
local ttl = tonumber(ARGV[5])

redis.call('ZREMRANGEBYSCORE', key, '-inf', cutoff)
local current = redis.call('ZCARD', key)

if current >= limit then
  local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
  if oldest[2] then
    return {0, current, oldest[2]}
  end
  return {0, current, 0}
end

redis.call('ZADD', key, now_score, member)
redis.call('EXPIRE', key, ttl)
return {1, current + 1, 0}
"""

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

    def _eval_atomic_check(
        self,
        *,
        key: str,
        cutoff: float,
        limit: int,
        now_score: float,
        member: str,
        ttl: int,
    ):
        client = self._get_client()
        return client.eval(
            self._ATOMIC_CHECK_SCRIPT,
            1,
            key,
            cutoff,
            limit,
            now_score,
            member,
            ttl,
        )

    def check(
        self,
        *,
        identifier: str,
        bucket: str,
        policy: RatePolicy,
        now: float,
    ) -> RateLimitDecision:
        key = f"parva:ratelimit:{bucket}:{identifier}"
        cutoff = now - policy.window_seconds
        member = f"{now:.6f}:{time.monotonic_ns()}"
        execution_results = self._eval_atomic_check(
            key=key,
            cutoff=cutoff,
            limit=policy.limit,
            now_score=now,
            member=member,
            ttl=policy.window_seconds,
        )

        if not isinstance(execution_results, (list, tuple)) or len(execution_results) != 3:
            raise RuntimeError("Redis rate limiter returned an unexpected result.")

        allowed_flag, current_count, oldest_score = execution_results
        allowed = bool(int(allowed_flag))
        current = int(current_count)

        if allowed:
            remaining = max(policy.limit - current, 0)
            return RateLimitDecision(allowed=True, remaining=remaining)

        retry_after = policy.window_seconds
        if oldest_score:
            retry_after = max(1, int(policy.window_seconds - (now - float(oldest_score))))
        return RateLimitDecision(allowed=False, remaining=0, retry_after=retry_after)


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
