"""In-memory request and cache metrics."""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from statistics import quantiles
from threading import Lock
from typing import Any, DefaultDict
from typing import Counter as CounterType


class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = Lock()
        self._requests: CounterType[str] = Counter()
        self._errors: CounterType[str] = Counter()
        self._throttles: CounterType[str] = Counter()
        self._latencies: DefaultDict[str, deque[float]] = defaultdict(lambda: deque(maxlen=256))
        self._cache_hits: CounterType[str] = Counter()
        self._cache_misses: CounterType[str] = Counter()

    def record_request(self, path: str, status_code: int, latency_ms: float) -> None:
        with self._lock:
            self._requests[path] += 1
            if status_code >= 400:
                self._errors[path] += 1
            self._latencies[path].append(float(latency_ms))

    def record_throttle(self, path: str) -> None:
        with self._lock:
            self._throttles[path] += 1

    def record_cache_lookup(self, cache_name: str, hit: bool) -> None:
        with self._lock:
            if hit:
                self._cache_hits[cache_name] += 1
            else:
                self._cache_misses[cache_name] += 1

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            endpoints = []
            for path, count in sorted(self._requests.items()):
                latencies = list(self._latencies.get(path, ()))
                p95 = None
                if len(latencies) >= 2:
                    p95 = round(quantiles(latencies, n=20)[-1], 2)
                elif latencies:
                    p95 = round(latencies[0], 2)
                endpoints.append(
                    {
                        "path": path,
                        "requests": count,
                        "errors": self._errors.get(path, 0),
                        "throttles": self._throttles.get(path, 0),
                        "p95_latency_ms": p95,
                    }
                )

            cache_names = sorted(set(self._cache_hits) | set(self._cache_misses))
            cache = {}
            for name in cache_names:
                hits = self._cache_hits.get(name, 0)
                misses = self._cache_misses.get(name, 0)
                total = hits + misses
                cache[name] = {
                    "hits": hits,
                    "misses": misses,
                    "hit_ratio": round(hits / total, 4) if total else None,
                }

            return {
                "endpoints": endpoints,
                "cache": cache,
            }


_registry = MetricsRegistry()


def get_metrics_registry() -> MetricsRegistry:
    return _registry
