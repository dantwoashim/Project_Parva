---
status: stable
tier: 1
lane: operations
last_verified: 2026-05-14
owner: platform-team
---

# Deployment Smoke

Deployment smoke checks verify that a live base URL is reachable, public-safe,
and serving the expected stable capabilities after deploy.

## Command

```bash
python scripts/release/deployment_smoke.py --base-url https://api.example.com
```

For local manual verification:

```bash
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
python scripts/release/deployment_smoke.py --base-url http://localhost:8000
```

## Checks

The smoke script checks:

- `/health`
- `/health/ready`
- `/v3/api/calendar/convert`
- `/v3/api/festivals/upcoming`
- `/v3/api/trust/capabilities`
- `/v3/api/protocol/version`
- `/v3/api/policy`
- `/openapi.json`
- a private Future-BS prediction route remains blocked

## Failure Policy

Fail the deploy if any stable public check returns the wrong status, the service
cannot be reached, or a private research route is exposed in a public profile.

If only a preview route is slow but correct, keep the deploy live only when the
route is not in the public critical path and the issue is documented in the
release notes.

## Evidence

When possible, write the smoke output to:

```text
tmp/deployment_smoke_local.json
```

Do not claim deployment smoke passed unless the command was run against an
available base URL and returned exit code 0.
