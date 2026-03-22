# Deployment

## Local
```bash
py -3.11 -m pip install -e .[test,dev]
uvicorn app.main:app --app-dir backend --reload --port 8000
npm --prefix frontend install
npm --prefix frontend run dev
```

## Supported runtime
- Python `3.11.x`
- Node version from `frontend/package-lock.json` compatible with `npm ci`

## Current build path
- Parva's supported build and deploy path uses `backend/` and `frontend/`.
- The old root `viral-sync` workspace residue has been removed.
- CI now includes a repo-hygiene guard to prevent that residue from coming back unnoticed.

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
- `PARVA_API_KEYS` (optional scoped API keys for non-public reads)
- `PARVA_TRUSTED_PROXY_IPS` (comma-separated proxy source IPs allowed to supply forwarded headers)

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

## CI gates
```bash
python scripts/release/check_repo_hygiene.py
python scripts/release/check_render_blueprint.py
python scripts/release/check_sdk_install.py
python scripts/validate_festival_catalog.py
python scripts/release/check_license_compliance.py
python -m pytest -q
python scripts/release/check_contract_freeze.py
python scripts/spec/run_conformance_tests.py
python scripts/release/generate_public_beta_artifacts.py --target 300 --computed-target 300
npm --prefix frontend run lint
npm --prefix frontend test -- --run
npm --prefix frontend run build
python scripts/run_browser_smoke.py
```

## Privacy-sensitive routes
- Personal Panchanga, Muhurta, Kundali, and Temporal Compass now support POST bodies for location and birth inputs.
- Responses on those routes are served with `Cache-Control: no-store`.
- Only trust `X-Forwarded-For` when the immediate sender IP is listed in `PARVA_TRUSTED_PROXY_IPS`.

## AGPL deployment requirement
- Production startup now fails if `PARVA_SOURCE_URL` is missing.
- `/source` redirects to the published corresponding source location.
- Responses include `X-Parva-License` and, when configured, a `Link: <...>; rel="source"` header.

## Release gate command
```bash
sh scripts/release/run_month9_release_gates.sh
```

## Public beta posture
- The current launch posture is public beta.
- Only claim what the generated evidence artifacts can currently prove.
- Keep `KNOWN_LIMITS.md` visible anywhere the product is presented as authoritative or explainable.

## Embed surfaces
- Static institutional widgets are published from `frontend/public/embed/`.
- Copy-paste usage is documented in `docs/EMBED_GUIDE.md`.
- Hosted API rollout guidance is in `docs/HOSTED_API_ONBOARDING.md`.
- Partner access and key provisioning are in `docs/PARTNER_ACCESS.md`.
- Render-specific bring-up is in `docs/RENDER_ZERO_BUDGET_RUNBOOK.md`.
- Commercial packaging guidance is in `docs/USAGE_TIERS.md`.
- Institution-facing launch gates are in `docs/INSTITUTIONAL_LAUNCH_CHECKLIST.md`.

## Clean source archive
```bash
py -3.11 scripts/release/package_source_archive.py
```

## Lean submission bundle
For academic/demo handoff where docs, tests, CI metadata, and raw source PDFs
are not needed:

```bash
py -3.11 scripts/release/package_submission_bundle.py
```
