# Deploy on Cloud Run

Use Cloud Run for the backend API only. The recommended production shape keeps the frontend on Cloudflare Pages and sets `PARVA_SERVE_FRONTEND=false` on Cloud Run.

## What this repo provides

- `Dockerfile.cloudrun` for a backend-only image
- `cloudbuild.cloudrun.yaml` for repeatable image builds in Google Cloud Build
- `scripts/release/check_cloudrun_blueprint.py` to validate the checked-in deployment assets

## Prerequisites

- a Google Cloud project with billing enabled
- Cloud Run API enabled
- Cloud Build API enabled
- Artifact Registry API enabled
- an Artifact Registry Docker repository in your target region
- a public source URL for `PARVA_SOURCE_URL`
- an Upstash Redis database or another managed Redis URL

## Recommended region

Choose one region and keep the backend image, Cloud Run service, and Redis as close together as practical. If you plan to use Cloud Run custom domain mapping, choose a region Google supports for that feature before you deploy.

## Build the backend image

Example Cloud Build invocation:

```bash
gcloud builds submit \
  --config cloudbuild.cloudrun.yaml \
  --substitutions _IMAGE=asia-southeast1-docker.pkg.dev/$PROJECT_ID/parva/project-parva-api:latest,_PARVA_PRECOMPUTE=0 \
  .
```

`_PARVA_PRECOMPUTE=0` keeps the image leaner and expects runtime configuration to use `PARVA_REQUIRE_PRECOMPUTED=false`.

## Deploy the service

Create one public web service from the built image. Keep the backend stateless and set these environment variables:

- `PARVA_ENV=production`
- `PARVA_LICENSE_MODE=AGPL-3.0-or-later`
- `PARVA_SOURCE_URL=<public repo or exact source archive>`
- `PARVA_SERVE_FRONTEND=false`
- `PARVA_RATE_LIMIT_ENABLED=true`
- `PARVA_RATE_LIMIT_BACKEND=redis`
- `PARVA_REDIS_URL=<your Upstash rediss:// URL>`
- `PARVA_REQUIRE_PRECOMPUTED=false`
- `PARVA_PLACE_SEARCH_ALLOW_REMOTE=false`
- `PARVA_PLACE_SEARCH_PROVIDER_CHAIN=offline`
- `PARVA_PLACE_SEARCH_PROVIDER_POLICY=offline_only`
- `CORS_ALLOW_ORIGINS=https://example.com,https://www.example.com`

Keep experimental routes disabled unless you explicitly need them:

- `PARVA_ENABLE_EXPERIMENTAL_API=false`
- `PARVA_ALLOW_EXPERIMENTAL_IN_PROD=false`

## Health checks

Use:

- `/health/live` for basic liveness
- `/health/ready` for readiness

Cloud Run injects the `PORT` environment variable. `Dockerfile.cloudrun` already respects that and defaults to `8080`.

## First deploy strategy

Do the first deploy on the default `*.run.app` hostname. Verify:

- `GET /health/live`
- `GET /health/ready`
- `GET /v3/api/calendar/today`
- `GET /v3/api/policy`

Only map a custom API domain after the default hostname is healthy.

## Custom domain

After the backend is healthy, add a custom domain such as `api.example.com` in Cloud Run and create the required DNS records in your DNS provider.

## Before cutover

- verify `CORS_ALLOW_ORIGINS` matches the exact frontend domains
- confirm `/source` resolves to your public source URL
- confirm rate limiting is using Redis rather than in-memory state
