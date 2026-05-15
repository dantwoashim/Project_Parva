# Performance Lane Fix

## Current State

The observed Future-BS performance artifact failure did not reproduce in the
current tree. Public-safe performance tests pass without removing coverage.

## Evidence

- `python -m pytest tests/performance -q -m "not private_source and not wide_corpus and not research_artifact" --maxfail=20`: 7 passed.
- `python scripts/perf/route_latency_smoke.py --profile public_reference --output reports/phase_08_performance_sre/latency_baseline.json`: pass.

The latency baseline report contains 6 routes, 0 failures, and 0 warnings.

## Boundary

Exact Future-BS prediction routes remain private/research-gated. Public
performance coverage is preserved for public-safe routes and metadata/capability
surfaces.

