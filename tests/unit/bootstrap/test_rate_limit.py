from __future__ import annotations

from app.bootstrap.rate_limit import RatePolicy, RedisRateLimiterBackend


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
