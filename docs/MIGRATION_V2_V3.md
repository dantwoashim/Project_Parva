# Migration Guide: v2 → v3

This guide covers migration from `/v2/api/*` to `/v3/api/*`.

## Timeline
- `v3` is the LTS track.
- `v2` remains available by default during migration.
- Optional hard cutoff can be enabled with:
  - `PARVA_DISABLE_V2=true` (returns `410 Gone` on `/v2/api/*`).

## Base URL changes
- Before: `http://localhost:8000/v2/api`
- After: `http://localhost:8000/v3/api`

## Contract notes
- Core response fields remain compatible.
- `policy` metadata is included across primary date endpoints.
- Explainability now has dedicated trace endpoints:
  - `GET /v3/api/explain/{trace_id}`

## Endpoint mapping
- `/v2/api/calendar/today` → `/v3/api/calendar/today`
- `/v2/api/calendar/convert` → `/v3/api/calendar/convert`
- `/v2/api/calendar/panchanga` → `/v3/api/calendar/panchanga`
- `/v2/api/festivals/{id}/explain` → `/v3/api/festivals/{id}/explain`
- `/v2/api/forecast/festivals` → `/v3/api/forecast/festivals`
- `/v2/api/provenance/*` → `/v3/api/provenance/*`

## SDK migration
- Python, TypeScript, and Go SDK defaults now target `/v3/api`.
- If needed, pass custom base URL to keep using `/v2/api` during transition.
