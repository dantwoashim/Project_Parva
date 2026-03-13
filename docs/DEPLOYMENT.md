# Deployment

## Local
```bash
py -3.11 -m pip install -e .[test,dev]
set PYTHONPATH=backend
uvicorn app.main:app --app-dir backend --reload --port 8000
npm --prefix frontend install
npm --prefix frontend run dev
```

## Supported runtime
- Python `3.11.x`
- Node version from `frontend/package-lock.json` compatible with `npm ci`

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
- `PARVA_ADMIN_TOKEN` (required for admin and experimental surfaces)
- `PARVA_API_KEYS` (optional scoped API keys for non-public reads)

## Removed from launch build
- `PARVA_ENABLE_WEBHOOKS` is intentionally unsupported in this build.
- Startup fails fast if it is set to `true`.

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
npm --prefix frontend run build
```
3. Publish frontend on GitHub Pages / Netlify / Vercel.

## Health checks
- `GET /health/live`
- `GET /health/ready`
- `GET /health/startup`
- `GET /v3/api/calendar/today`
- `GET /v3/api/festivals/upcoming?days=30`

## CI gates
```bash
python -m pytest -q
python scripts/release/check_contract_freeze.py
python scripts/spec/run_conformance_tests.py
npm --prefix frontend run lint
npm --prefix frontend test -- --run
npm --prefix frontend run build
```

## Release gate command
```bash
sh scripts/release/run_month9_release_gates.sh
```

## Clean source archive
```bash
py -3.11 scripts/release/package_source_archive.py
```
