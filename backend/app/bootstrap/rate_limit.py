"""Rate-limit backend abstractions and implementations."""

from __future__ import annotations

import time
from collections import OrderedDict, deque
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


class RateLimiterUnavailable(RuntimeError):
    """Raised when a selected shared limiter cannot make a safe decision."""


@dataclass
class _MemoryBucket:
    entries: deque[float]
    expires_at: float


class InMemoryRateLimiterBackend:
    """Bounded in-process rate limiter for one-worker deployments."""

    def __init__(self, *, max_buckets: int = 10_000) -> None:
        if max_buckets < 1:
            raise ValueError("In-memory rate limiter max_buckets must be positive.")
        self._lock = Lock()
        self._max_buckets = max_buckets
        self._buckets: OrderedDict[tuple[str, str], _MemoryBucket] = OrderedDict()

    @property
    def bucket_count(self) -> int:
        with self._lock:
            return len(self._buckets)

    def _evict_expired(self, now: float) -> None:
        expired = [key for key, state in self._buckets.items() if state.expires_at <= now]
        for key in expired:
            self._buckets.pop(key, None)

    def _new_bucket(self, bucket_key: tuple[str, str], now: float) -> _MemoryBucket:
        self._evict_expired(now)
        if len(self._buckets) >= self._max_buckets:
            self._buckets.popitem(last=False)
        state = _MemoryBucket(entries=deque(), expires_at=now)
        self._buckets[bucket_key] = state
        return state

    def check(
        self,
        *,
        identifier: str,
        bucket: str,
        policy: RatePolicy,
        now: float,
    ) -> RateLimitDecision:
        if policy.limit < 1 or policy.window_seconds < 1:
            raise ValueError("Rate-limit policy requires positive limit and window_seconds.")
        bucket_key = (bucket, identifier)
        with self._lock:
            state = self._buckets.get(bucket_key)
            if state is None:
                state = self._new_bucket(bucket_key, now)
            else:
                self._buckets.move_to_end(bucket_key)
            entries = state.entries
            cutoff = now - policy.window_seconds
            while entries and entries[0] <= cutoff:
                entries.popleft()

            if len(entries) >= policy.limit:
                retry_after = max(1, int(policy.window_seconds - (now - entries[0])))
                return RateLimitDecision(allowed=False, remaining=0, retry_after=retry_after)

            entries.append(now)
            state.expires_at = now + policy.window_seconds
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
        try:
            execution_results = self._eval_atomic_check(
                key=key,
                cutoff=cutoff,
                limit=policy.limit,
                now_score=now,
                member=member,
                ttl=policy.window_seconds,
            )
        except Exception as exc:  # noqa: BLE001 - fail closed when the shared limiter is unavailable.
            raise RateLimiterUnavailable(
                "Redis rate limiter is unavailable; request denied by fail-closed policy."
            ) from exc

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
    memory_max_buckets: int = 10_000,
) -> RateLimiterBackend:
    normalized = (backend_name or "memory").strip().lower()
    if normalized == "memory":
        return InMemoryRateLimiterBackend(max_buckets=memory_max_buckets)
    if normalized == "redis":
        return RedisRateLimiterBackend(redis_url or "")
    raise ValueError(
        "PARVA_RATE_LIMIT_BACKEND must be one of: memory, redis."
    )
