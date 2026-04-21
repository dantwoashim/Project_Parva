# Operator Quickstart

This quickstart is for operators deploying Project Parva as a production-style API platform.

## 1. Prepare configuration

- publish corresponding source and set `PARVA_SOURCE_URL`
- configure Redis and set `PARVA_RATE_LIMIT_BACKEND=redis`
- choose a place-search policy:
  - `offline_only`
  - or `acknowledged_remote`

## 2. Validate locally or in CI

```bash
make verify
make preflight-production
```

## 3. Smoke check the runtime

- `GET /health/live`
- `GET /health/ready`
- `GET /source`
- `GET /v3/api/policy`
- `GET /v3/api/calendar/today`

## 4. Know the product posture

- the stable public platform is `/v3/api/*`
- `/api/*` is compatibility only
- the frontend is a reference beta
- preview and experimental surfaces should not be marketed as core product behavior

## 5. Keep runbooks close

Before public traffic, read:

- `docs/runbooks/redis-outage.md`
- `docs/runbooks/source-publication-missing.md`
- `docs/runbooks/precompute-artifact-failure.md`
- `docs/runbooks/provider-degradation.md`
- `docs/runbooks/release-rollback.md`
