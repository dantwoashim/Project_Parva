# Deployment

Project Parva should be deployed as a stable API platform with a clearly labeled reference frontend, not as an ambiguous all-in-one product shell.

## Local
```bash
py -3.11 -m pip install -e .[test,dev]
uvicorn app.main:app --app-dir backend --reload --port 8000
npm --prefix frontend ci
npm --prefix frontend run dev
```

## Supported runtime
- Python `3.11.x`
- Node version from `frontend/package-lock.json` compatible with `npm ci`

## Current build path
- Parva's supported build and deploy path uses `backend/` and `frontend/`.

## Environment variables
- `CORS_ALLOW_ORIGINS` (comma-separated)
- `PARVA_ENABLE_EXPERIMENTAL_API` (`true|false`, default `false`)
- `PARVA_ALLOW_EXPERIMENTAL_IN_PROD` (`true|false`, default `false`)
- `PARVA_ENV` (`development|production`)
- `PARVA_MAX_REQUEST_BYTES` (default `1048576`)
- `PARVA_MAX_QUERY_LENGTH` (default `4096`)
- `PARVA_RATE_LIMIT_ENABLED` (`true|false`, default `true`)
- `PARVA_SERVE_FRONTEND` (`true|false`, default `false`)
- `PARVA_FRONTEND_DIST` (optional path for built frontend)
- `PARVA_LICENSE_MODE` (`AGPL-3.0-or-later`, default and required for the zero-budget path)
- `PARVA_SOURCE_URL` (required in production; public repo or source archive URL for the deployed build)
- `PARVA_ADMIN_TOKEN` (required for admin and experimental surfaces)
- `PARVA_API_KEYS` (optional scoped API keys for preview tracks, partner overlays, or admin surfaces)
- `PARVA_TRUSTED_PROXY_IPS` (comma-separated proxy source IPs allowed to supply forwarded headers)
- `PARVA_PLACE_SEARCH_PROVIDER_CHAIN` (default `offline,nominatim`)
- `PARVA_PLACE_SEARCH_ALLOW_REMOTE` (`true|false`, default `true`)
- `PARVA_PLACE_SEARCH_PROVIDER_POLICY` (`offline_only|acknowledged_remote`, required in production)
- `PARVA_PLACE_SEARCH_TIMEOUT_SECONDS` (single-attempt upstream timeout)
- `PARVA_PLACE_SEARCH_TIME_BUDGET_SECONDS` (overall geocoder time budget)
- `PARVA_PLACE_SEARCH_RETRY_ATTEMPTS` (default `2`)
- `PARVA_PLACE_SEARCH_RETRY_BACKOFF_SECONDS` (default `0.3`)
- `PARVA_PLACE_SEARCH_CACHE_TTL_SECONDS` (default `3600`)

## Production minimums

Every serious deployment should meet these minimums before it is considered supported:

- canonical public traffic goes through `/v3/api/*`
- `PARVA_SOURCE_URL` is configured
- `PARVA_RATE_LIMIT_BACKEND=redis`
- `PARVA_REDIS_URL` is configured
- required precomputed artifacts are either present or intentionally disabled with `PARVA_REQUIRE_PRECOMPUTED=false`
- experimental routes remain disabled unless there is an explicit reason to enable them
- place search policy is explicit:
  - `PARVA_PLACE_SEARCH_PROVIDER_POLICY=offline_only` for privacy-first production
  - or `PARVA_PLACE_SEARCH_PROVIDER_POLICY=acknowledged_remote` if the operator knowingly allows remote geocoding

Run the production preflight locally or in CI with:

```bash
make preflight-production
```

## Provider posture

- Treat deployment as provider-neutral. The repo hardening gates validate runtime requirements, not just one host.
- `render.yaml` may remain as a legacy example, but it is not the canonical production control surface.
- The recommended hosted split is:
  - Cloudflare Pages for `frontend/`
  - Cloud Run for the backend container
  - Upstash Redis for distributed rate limiting

## Recommended hosted split

Use this shape unless you have a stronger operator reason not to:

1. Deploy the backend container with `Dockerfile.cloudrun`.
2. Build and host the frontend separately on Cloudflare Pages.
3. Set `PARVA_SERVE_FRONTEND=false` in hosted backend environments.
4. Keep `PARVA_RATE_LIMIT_BACKEND=redis` with `PARVA_REDIS_URL` set to a managed Redis URL such as Upstash.
5. Set `CORS_ALLOW_ORIGINS` to the exact frontend domains you intend to serve.

Reference files included in the repo:

- `Dockerfile.cloudrun`
- `cloudbuild.cloudrun.yaml`
- `frontend/public/_redirects`

Reference docs:

- [DEPLOY_CLOUD_RUN.md](DEPLOY_CLOUD_RUN.md)
- [DEPLOY_CLOUDFLARE_PAGES.md](DEPLOY_CLOUDFLARE_PAGES.md)
- [DEPLOY_UPSTASH.md](DEPLOY_UPSTASH.md)

## Reference frontend

- The frontend should be described as a public reference beta unless and until account/sync/member-state workflows are explicitly productized.
- If `PARVA_SERVE_FRONTEND=true`, treat that as a convenience delivery mode, not proof that the frontend is a fully supported consumer product.

## Split frontend/backend deployment

1. Deploy the backend on your chosen container/web-service runtime.
2. Build the frontend with a production API base:
```bash
set VITE_API_BASE=https://api.example.com/v3/api
set VITE_SOURCE_URL=https://github.com/<you>/<your-public-parva-fork>
npm --prefix frontend run build
```
3. Publish the frontend on your static host of choice.

For Cloudflare Pages specifically, the repo already includes `frontend/public/_redirects` so client-side routing works after deploy.

## Health checks
- `GET /health/live`
- `GET /health/ready`
- `GET /health/startup`
- `GET /source`
- `GET /v3/api/calendar/today`
- `GET /v3/api/festivals/upcoming?days=30`

## Geocoding posture

- Default provider chain: offline Nepal gazetteer first, remote geocoder second.
- In production, set `PARVA_PLACE_SEARCH_PROVIDER_POLICY` explicitly and keep it aligned with `PARVA_PLACE_SEARCH_ALLOW_REMOTE` and `PARVA_PLACE_SEARCH_PROVIDER_CHAIN`.
- For serious production traffic, replace the public remote provider with a self-hosted or paid upstream.
- Keep provider time budgets and retries conservative so place search cannot dominate request latency.

## Legacy Render note

- `render.yaml` is kept as a legacy deployment example only.
- If you still use Render, validate it with `python scripts/release/check_render_blueprint.py`.
- Do not treat Render-specific settings as the only supported production path.
- The split-hosting path should also pass `python scripts/release/check_cloudrun_blueprint.py`.

## CI gates
```bash
python scripts/release/check_repo_hygiene.py
python scripts/release/check_render_blueprint.py
python scripts/release/check_cloudrun_blueprint.py
python scripts/release/check_sdk_install.py
python scripts/validate_festival_catalog.py
python scripts/release/check_license_compliance.py
python -m pytest -q
python scripts/release/check_contract_freeze.py
python scripts/release/check_documented_routes.py
python scripts/spec/run_conformance_tests.py
npm --prefix frontend run lint
npm --prefix frontend test -- --run
npm --prefix frontend run build
python scripts/run_browser_smoke.py
```

## Privacy-sensitive routes
- Personal Panchanga, Muhurta, Kundali, and Temporal Compass now support POST bodies for location and birth inputs.
- Responses on those routes are served with `Cache-Control: no-store`.
- Only trust `X-Forwarded-For` when the immediate sender IP is listed in `PARVA_TRUSTED_PROXY_IPS`.
- The supported `v3` read and compute surface is public by default; use `/v3/api/policy` for the generated route-access summary.

## AGPL deployment requirement
- Production startup now fails if `PARVA_SOURCE_URL` is missing.
- `/source` redirects to the published corresponding source location.
- Responses include `X-Parva-License` and, when configured, a `Link: <...>; rel="source"` header.

## Release gate command
```bash
sh scripts/release/run_month9_release_gates.sh
```

## Embed surfaces
- Static institutional widgets are published from `frontend/public/embed/`.
- Copy-paste usage is documented in `docs/EMBED_GUIDE.md`.
- API request examples are documented in `docs/API_QUICKSTART.md`.
- Product-facing constraints and caveats are documented in `docs/KNOWN_LIMITS.md`.

## Clean source archive
```bash
py -3.11 scripts/release/package_source_archive.py
```

## Lean submission bundle
For lightweight handoff where docs, tests, CI metadata, and raw source PDFs are not needed:

```bash
py -3.11 scripts/release/package_submission_bundle.py
```
