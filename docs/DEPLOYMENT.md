# Deployment

## Local
```bash
# backend
cd /Users/rohanbasnet14/Documents/Project_Parva
PYTHONPATH=backend uvicorn app.main:app --app-dir backend --reload --port 8000

# frontend
cd /Users/rohanbasnet14/Documents/Project_Parva/frontend
npm install
npm run dev
```

## Environment variables
- `CORS_ALLOW_ORIGINS` (comma-separated)
- `PARVA_ENABLE_EXPERIMENTAL_API` (`true|false`, default `false`)
- `PARVA_ENV` (`development|production`)
- `PARVA_MAX_REQUEST_BYTES` (default `1048576`)
- `PARVA_MAX_QUERY_LENGTH` (default `4096`)
- `PARVA_SERVE_FRONTEND` (`true|false`, default `false`)
- `PARVA_FRONTEND_DIST` (optional absolute path for built frontend)

## Recommended Zero-Dollar Deploy (Single Place)
This is the best practical zero-budget setup for the current stack:

- One Render free web service
- Frontend + backend served from the same container/domain
- API under `/v3/api/*`
- UI served at `/`

### Steps
1. Push latest code to GitHub.
2. In Render, create **Blueprint** from repo (`/Users/rohanbasnet14/Documents/Project_Parva/render.yaml`).
3. Confirm environment:
   - `PARVA_ENABLE_EXPERIMENTAL_API=false`
   - `PARVA_ENV=production`
   - `PARVA_SERVE_FRONTEND=true`
4. Deploy.
5. Smoke-check:
```bash
python3 scripts/live_smoke.py --base https://<your-render-service>.onrender.com
```

## Cloudflare note (important)
- Cloudflare Pages is excellent for static frontend hosting.
- The current backend uses Python + `pyswisseph`, which is not a straightforward fit for Cloudflare Pages Functions/Workers runtime.
- If you want Cloudflare now, use it for frontend/static artifacts; keep dynamic API on Render.

## Legacy split deploy (if needed)
1. Deploy backend on Render.
2. Build frontend with production API base:
```bash
cd /Users/rohanbasnet14/Documents/Project_Parva/frontend
VITE_API_BASE=https://<your-render-service>.onrender.com/v3/api npm run build
```
3. Publish frontend on GitHub Pages / Netlify / Vercel.

## Health checks
- `GET /health`
- `GET /v3/api/calendar/today`
- `GET /v3/api/festivals/upcoming?days=30`

## CI gates
```bash
cd /Users/rohanbasnet14/Documents/Project_Parva
PYTHONPATH=backend python3 -m pytest -q
PYTHONPATH=backend python3 scripts/release/check_contract_freeze.py
PYTHONPATH=backend python3 scripts/spec/run_conformance_tests.py
cd frontend && npm run build
```

## Release gate command
```bash
cd /Users/rohanbasnet14/Documents/Project_Parva
bash scripts/release/run_month9_release_gates.sh
```
