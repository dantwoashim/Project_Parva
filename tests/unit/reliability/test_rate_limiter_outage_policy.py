from __future__ import annotations

import pytest
from app.bootstrap.rate_limit import RateLimiterUnavailable, RatePolicy, RedisRateLimiterBackend


def test_redis_rate_limiter_fails_closed_when_backend_unavailable():
    backend = RedisRateLimiterBackend.__new__(RedisRateLimiterBackend)

    def _raise(**_kwargs):
        raise RuntimeError("redis unavailable")

    backend._eval_atomic_check = _raise

    with pytest.raises(RateLimiterUnavailable):
        backend.check(
            identifier="user-1",
            bucket="public",
            policy=RatePolicy(limit=1, window_seconds=60),
            now=1_700_000_000.0,
        )
