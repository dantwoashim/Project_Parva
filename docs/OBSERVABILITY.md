---
status: stable
tier: 1
lane: operations
last_verified: 2026-05-14
owner: platform-team
---

# Observability

Project Parva exposes basic request tracing, structured logs, and in-process
metrics for public and preview operations.

## Request And Trace IDs

Incoming `X-Request-ID` is preserved. If the header is absent, middleware
generates an ID. Responses include:

```text
X-Request-ID
X-Trace-ID
```

For now both values are the same request-scoped identifier. Future
OpenTelemetry integration can map `X-Trace-ID` to a distributed trace while
keeping `X-Request-ID` as the caller-visible correlation key.

## Structured Logs

Request middleware logs JSON records with:

- `event`
- `request_id`
- `path`
- `method`
- `status_code`
- `latency_ms`
- `principal`
- `client_ip`
- `version`

Security and rate-limit events also include policy, bucket, and denial reason
fields. Logs must not include private source paths, credentials, raw payment
details, or private Future-BS artifacts.

## Metrics Endpoints

| Endpoint | Purpose |
| --- | --- |
| `/v3/api/reliability/metrics` | JSON runtime status plus request, error, throttle, cache, and degraded-state metrics. |
| `/v3/api/reliability/metrics.prom` | Prometheus text exposition for the same in-process counters. |

Tracked metric scopes:

- route request counts
- route error counts
- route throttle counts
- route p95 latency over recent samples
- cache hit and miss counts
- degraded runtime states

## Cache Metrics

The Phase 08 observance resolver records `observance_resolution` cache hits and
misses. Festival and precomputed artifact caches should be added to this same
registry as their cache adapters are promoted.

## Dashboard Starter

Initial SLO dashboard panels:

| Panel | Query or source |
| --- | --- |
| API availability | 5xx rate by route family. |
| p95 latency | `parva_request_latency_p95_ms` grouped by path. |
| Rate limit pressure | `parva_request_throttles_total`. |
| Cache effectiveness | `parva_cache_hit_ratio`. |
| Degraded states | `parva_degraded_state_total`. |
| Trust freshness | Scheduled trust drift workflow result and trust verification status. |

## PII Scrubbing

Do not log request bodies by default. When debugging billing, admin, provenance,
or private research routes, log stable identifiers and policy outcomes rather
than emails, tokens, source paths, or uploaded payload content.

## OpenTelemetry Direction

OpenTelemetry is practical once deployment has a collector target. The first
integration should instrument FastAPI request spans, outbound source fetches,
precompute jobs, and trust verification scripts. Until then, the JSON logs and
Prometheus endpoint provide a minimal but auditable baseline.
