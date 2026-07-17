from __future__ import annotations

from app.bootstrap.rate_limit import (
    InMemoryRateLimiterBackend,
    RatePolicy,
    RedisRateLimiterBackend,
)


class _FakeRedis:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def eval(self, script, numkeys, *args):
        self.calls.append((script, numkeys, args))
        return self.result


def _backend_with_result(result):
    backend = RedisRateLimiterBackend.__new__(RedisRateLimiterBackend)
    backend._redis_url = "redis://example.test/0"
    backend._client = _FakeRedis(result)
    return backend


def test_redis_rate_limiter_uses_single_atomic_eval():
    backend = _backend_with_result([1, 2, 0])

    decision = backend.check(
        identifier="demo",
        bucket="calendar",
        policy=RatePolicy(limit=3, window_seconds=60),
        now=1000.0,
    )

    assert decision.allowed is True
    assert decision.remaining == 1
    assert len(backend._client.calls) == 1
    script, numkeys, args = backend._client.calls[0]
    assert "ZREMRANGEBYSCORE" in script
    assert "ZADD" in script
    assert numkeys == 1
    assert args[0] == "parva:ratelimit:calendar:demo"


def test_redis_rate_limiter_denies_and_computes_retry_after_from_oldest_score():
    backend = _backend_with_result([0, 5, 990.0])

    decision = backend.check(
        identifier="demo",
        bucket="calendar",
        policy=RatePolicy(limit=5, window_seconds=60),
        now=1000.0,
    )

    assert decision.allowed is False
    assert decision.remaining == 0
    assert decision.retry_after == 50


def test_memory_rate_limiter_enforces_policy() -> None:
    backend = InMemoryRateLimiterBackend(max_buckets=10)
    policy = RatePolicy(limit=2, window_seconds=60)

    assert backend.check(identifier="client", bucket="api", policy=policy, now=1.0).allowed
    assert backend.check(identifier="client", bucket="api", policy=policy, now=2.0).allowed
    denied = backend.check(identifier="client", bucket="api", policy=policy, now=3.0)

    assert denied.allowed is False
    assert denied.retry_after == 58


def test_memory_rate_limiter_evicts_lru_buckets_at_capacity() -> None:
    backend = InMemoryRateLimiterBackend(max_buckets=3)
    policy = RatePolicy(limit=2, window_seconds=60)

    for identifier in ("a", "b", "c", "d", "e"):
        backend.check(identifier=identifier, bucket="api", policy=policy, now=1.0)

    assert backend.bucket_count == 3
    first_request_after_eviction = backend.check(
        identifier="a",
        bucket="api",
        policy=policy,
        now=2.0,
    )
    assert first_request_after_eviction.allowed is True
    assert first_request_after_eviction.remaining == 1
    assert backend.bucket_count == 3


def test_memory_rate_limiter_removes_expired_buckets_before_eviction() -> None:
    backend = InMemoryRateLimiterBackend(max_buckets=2)
    policy = RatePolicy(limit=1, window_seconds=10)
    backend.check(identifier="a", bucket="api", policy=policy, now=1.0)
    backend.check(identifier="b", bucket="api", policy=policy, now=1.0)

    backend.check(identifier="c", bucket="api", policy=policy, now=12.0)

    assert backend.bucket_count == 1
