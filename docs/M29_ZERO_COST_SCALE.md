# M29 Zero-Cost Scale Playbook (Year 3 Week 17-20)

## Precompute Pipeline
- Generate panchanga + festival artifacts:
  - `python3 scripts/precompute/precompute_all.py --start-year 2026 --end-year 2028`
- Artifacts written to:
  - `/Users/rohanbasnet14/Documents/Project Parva/output/precomputed/panchanga_YYYY.json`
  - `/Users/rohanbasnet14/Documents/Project Parva/output/precomputed/festivals_YYYY.json`

## Runtime Cache Paths
- `/api/calendar/panchanga` checks precomputed yearly files first.
- `/api/calendar/panchanga/range` computes cache hit ratio per request.
- `/api/calendar/festivals/upcoming` uses precomputed yearly festival artifacts when available.
- `/api/cache/stats` exposes artifact inventory and yearly coverage.

## Performance / Load Commands
- Profile hot endpoints:
  - `python3 scripts/precompute/profile_endpoints.py --iterations 20`
- Load-test cache behavior:
  - `python3 scripts/precompute/loadtest_cache.py --requests 1000 --concurrency 30 --start-date 2026-01-01 --days 365`

## Generated Reports
- `/Users/rohanbasnet14/Documents/Project Parva/reports/m29_profile.json`
- `/Users/rohanbasnet14/Documents/Project Parva/reports/loadtest_m29.json`

## Current Snapshot
- Cache hit ratio (panchanga load test): `1.0`
- P95 latency: `< 500ms` target met in local in-process run
- Simulated throughput: `>1000 req/min` equivalent achieved on free-tier-style setup
