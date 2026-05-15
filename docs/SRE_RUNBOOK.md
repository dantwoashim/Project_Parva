# SRE Runbook

Project Parva SRE work protects public calendar infrastructure from silent
latency, availability, data freshness, and trust verification regressions.

## Initial SLOs

| Area | Target |
| --- | --- |
| Public API availability | 99.5 percent monthly for stable public routes. |
| Health endpoint p95 | Less than 100 ms deployed. |
| Calendar conversion p95 | Less than 200 ms deployed. |
| Festivals upcoming p95 warm | Less than 500 ms deployed. |
| Error rate | Less than 1 percent 5xx over 30 minutes. |
| Trust verification freshness | Trust drift check at least daily. |
| Precomputed artifact freshness | Review stale artifacts after 30 days unless release-pinned. |

## Error Budget

If a stable public route exhausts 50 percent of its monthly error budget in one
day, freeze non-critical deploys until the route is back under budget and the
incident notes identify a direct remediation.

## Incident Steps

1. Confirm whether `/health/live` and `/health/ready` disagree.
2. Check recent deploy version, route profile, and `PARVA_ENV`.
3. Check `/v3/api/reliability/metrics` and `/v3/api/reliability/metrics.prom`.
4. Run `scripts/release/deployment_smoke.py` against the affected base URL.
5. If calendar, festival, or panchanga routes are slow, verify precomputed
   artifact availability and cache warm status.
6. If trust, protocol, or source routes fail, run the trust verification scripts
   before serving new release claims.
7. Roll back if a stable route returns sustained 5xx responses, exposes private
   data, or serves misleading trust/source metadata.

## Known Failure Modes

| Failure | Response |
| --- | --- |
| Rate limiter unavailable in production | Fail closed, surface 503, restore Redis or disable only in a controlled non-production profile. |
| Precomputed artifacts missing | Serve clear degraded metadata or regenerate artifacts. Do not silently claim generated data exists. |
| JPL kernel unavailable | Use precomputed trusted artifacts or Swiss/Moshier fallback with explicit metadata. |
| Festival cold cache slow | Prewarm hot set at startup and move annual windows to release artifacts. |
| TimeGraph or Impact response grows | Enforce limits and migrate to persistent indexed storage. |

## Escalation Roles

| Role | Responsibility |
| --- | --- |
| Release owner | Decide deploy freeze, rollback, or release artifact regeneration. |
| Calendar domain owner | Review BS/AD, panchanga, festival, and source policy correctness. |
| Security owner | Review private route exposure, PII, credentials, and auth failures. |
| SRE owner | Own latency, availability, smoke tests, metrics, and incident review. |

## Performance Commands

```bash
python scripts/perf/route_latency_smoke.py --profile public_reference --output tmp/public_reference_latency_baseline.json
python -m pytest tests/performance -q
python -m pytest tests/integration/test_heavy_compute_offload.py -q
python scripts/release/check_backend_smoke.py
python scripts/release/deployment_smoke.py --base-url http://localhost:8000
python scripts/release/verify_public.py
npm --prefix frontend run build
```
