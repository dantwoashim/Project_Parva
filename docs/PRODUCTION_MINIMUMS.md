# Production Minimums

Use this checklist before calling a deployment production-ready for the intended public API scope.

## Required runtime settings

- `PARVA_ENV=production`
- `PARVA_LICENSE_MODE=AGPL-3.0-or-later`
- `PARVA_SOURCE_URL=<public repo or source archive>`
- `PARVA_RATE_LIMIT_BACKEND=redis`
- `PARVA_REDIS_URL=<redis url>`
- `PARVA_ENABLE_EXPERIMENTAL_API=false` unless there is an explicit preview rollout
- `PARVA_PLACE_SEARCH_PROVIDER_POLICY=offline_only` or `acknowledged_remote`

## Required operational conditions

- precomputed artifacts are present when the policy requires them
- readiness passes at `/health/ready`
- `/source` resolves to corresponding source
- route policy summary is available at `/v3/api/policy`
- private/location-sensitive routes remain `Cache-Control: no-store`

## Required validation commands

```bash
make verify
make preflight-production
```

## Required product positioning

- `/v3/api/*` is presented as the canonical public contract
- `/api/*` is treated as compatibility only
- `/v2`, `/v4`, `/v5` are described as experimental
- the frontend is described as a public reference beta unless separately productized
