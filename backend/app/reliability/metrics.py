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
        self._degraded_states: CounterType[str] = Counter()

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

    def record_degraded_state(self, reason: str) -> None:
        with self._lock:
            self._degraded_states[reason] += 1

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
                "degraded_states": dict(sorted(self._degraded_states.items())),
            }

    def to_prometheus(self) -> str:
        snapshot = self.snapshot()
        lines = [
            "# HELP parva_requests_total Total API requests by path",
            "# TYPE parva_requests_total counter",
        ]
        for row in snapshot["endpoints"]:
            path = row["path"].replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'parva_requests_total{{path="{path}"}} {row["requests"]}')
            lines.append(f'parva_request_errors_total{{path="{path}"}} {row["errors"]}')
            lines.append(f'parva_request_throttles_total{{path="{path}"}} {row["throttles"]}')
            if row["p95_latency_ms"] is not None:
                lines.append(f'parva_request_latency_p95_ms{{path="{path}"}} {row["p95_latency_ms"]}')
        lines.extend(
            [
                "# HELP parva_cache_hits_total Cache hits by cache name",
                "# TYPE parva_cache_hits_total counter",
            ]
        )
        for name, row in snapshot["cache"].items():
            escaped = name.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'parva_cache_hits_total{{cache="{escaped}"}} {row["hits"]}')
            lines.append(f'parva_cache_misses_total{{cache="{escaped}"}} {row["misses"]}')
            if row["hit_ratio"] is not None:
                lines.append(f'parva_cache_hit_ratio{{cache="{escaped}"}} {row["hit_ratio"]}')
        lines.extend(
            [
                "# HELP parva_degraded_state_total Degraded runtime states observed",
                "# TYPE parva_degraded_state_total counter",
            ]
        )
        for reason, count in snapshot["degraded_states"].items():
            escaped = reason.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'parva_degraded_state_total{{reason="{escaped}"}} {count}')
        return "\n".join(lines) + "\n"


_registry = MetricsRegistry()


def get_metrics_registry() -> MetricsRegistry:
    return _registry
