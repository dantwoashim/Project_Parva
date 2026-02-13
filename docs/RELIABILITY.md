# Reliability Guide (Year 3 Week 21-24)

## SLO Targets
- Availability target: `99.5%` monthly (service-level objective)
- Latency target: `P95 < 500ms`
- Differential drift gate: `<= 2.0%` major differences
- Cache target: panchanga cache-hit ratio `>= 90%`

## Reliability Endpoints
- `GET /v2/api/reliability/status`
- `GET /v2/api/reliability/slos`
- `GET /v2/api/reliability/playbooks`

## Incident Playbooks
### 1) Ephemeris Unavailable
- Symptom: ephemeris compute errors or fallback mode
- Action:
  - Serve precomputed artifacts where possible (`/api/calendar/panchanga`, upcoming festivals)
  - Mark outputs with degraded status
  - Regenerate artifacts using:
    - `python3 scripts/precompute/precompute_all.py --start-year <Y> --end-year <Y+2>`

### 2) Cache Artifact Missing
- Symptom: `/api/cache/stats` shows no files or missing year
- Action:
  - Re-run precompute scripts
  - Validate cache path and artifact permissions

### 3) Source Outage
- Symptom: external reference updates delayed/unavailable
- Action:
  - Continue serving computed outputs
  - Annotate source freshness in reporting pipelines
  - Schedule backfill when source recovers
