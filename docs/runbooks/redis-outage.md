# Runbook: Redis Outage

## Signal

- readiness fails or rate limiting degrades in production
- logs show Redis client or rate-limit backend errors

## Immediate action

- verify Redis reachability and credentials
- confirm `PARVA_RATE_LIMIT_BACKEND=redis`
- confirm `PARVA_REDIS_URL` is present and correct

## Mitigation

- restore Redis connectivity first
- do not silently switch production to in-memory rate limiting unless the operator is intentionally accepting degraded single-instance behavior

## Verification

- `GET /health/ready`
- `GET /v3/api/policy`
- a normal public read route such as `/v3/api/calendar/today`
