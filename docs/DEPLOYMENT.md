# Deployment

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
- `PARVA_PLACE_SEARCH_TIMEOUT_SECONDS` (single-attempt upstream timeout)
- `PARVA_PLACE_SEARCH_TIME_BUDGET_SECONDS` (overall geocoder time budget)
- `PARVA_PLACE_SEARCH_RETRY_ATTEMPTS` (default `2`)
- `PARVA_PLACE_SEARCH_RETRY_BACKOFF_SECONDS` (default `0.3`)
- `PARVA_PLACE_SEARCH_CACHE_TTL_SECONDS` (default `3600`)

## Recommended Zero-Dollar Deploy (Single Place)
This is the best practical zero-budget setup for the current stack:

- One Render free web service
- Frontend + backend served from the same container/domain
- API under `/v3/api/*`
- UI served at `/`

### Steps
1. Push latest code to GitHub.
2. In Render, create a Blueprint from `render.yaml`.
3. Confirm environment:
   - `PARVA_ENABLE_EXPERIMENTAL_API=false`
   - `PARVA_ENV=production`
   - `PARVA_SERVE_FRONTEND=true`
   - `PARVA_SOURCE_URL=https://github.com/<you>/<your-public-parva-fork>`
4. Deploy.
5. Smoke-check:
```bash
python scripts/live_smoke.py --base https://<your-render-service>.onrender.com
```

## Cloudflare note (important)
- Cloudflare Pages is excellent for static frontend hosting.
- The current backend uses Python + `pyswisseph`, which is not a straightforward fit for Cloudflare Pages Functions/Workers runtime.
- If you want Cloudflare now, use it for the frontend static site; keep the dynamic API on Render.

## Legacy split deploy (if needed)
1. Deploy backend on Render.
2. Build frontend with production API base:
```bash
set VITE_API_BASE=https://<your-render-service>.onrender.com/v3/api
set VITE_SOURCE_URL=https://github.com/<you>/<your-public-parva-fork>
npm --prefix frontend run build
```
3. Publish frontend on GitHub Pages / Netlify / Vercel.

## Health checks
- `GET /health/live`
- `GET /health/ready`
- `GET /health/startup`
- `GET /source`
- `GET /v3/api/calendar/today`
- `GET /v3/api/festivals/upcoming?days=30`

## Geocoding posture

- Default provider chain: offline Nepal gazetteer first, remote geocoder second.
- For serious production traffic, replace the public remote provider with a self-hosted or paid upstream.
- Keep provider time budgets and retries conservative so place search cannot dominate request latency.

## CI gates
```bash
python scripts/release/check_repo_hygiene.py
python scripts/release/check_render_blueprint.py
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
