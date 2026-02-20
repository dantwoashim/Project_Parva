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
- `PARVA_MAX_REQUEST_BYTES` (default `1048576`)
- `PARVA_MAX_QUERY_LENGTH` (default `4096`)

## Free-tier deployment profile
1. Frontend: GitHub Pages or Netlify/Vercel free tier.
2. Backend: Render/Railway/Fly free tier.
3. Static artifacts (`reports`, precomputed JSON) served from GitHub Pages.

## Health checks
- `GET /health`
- `GET /v3/api/reliability/status`

## CI gates
```bash
PYTHONPATH=backend python3 -m pytest -q
PYTHONPATH=backend python3 scripts/release/check_contract_freeze.py
PYTHONPATH=backend python3 scripts/spec/run_conformance_tests.py
cd frontend && npm run build
```
