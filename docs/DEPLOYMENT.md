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

## Production (Zero Budget) Checklist
1. Push latest code and tag to GitHub.
2. Deploy backend on Render free tier using `/Users/rohanbasnet14/Documents/Project_Parva/render.yaml`.
3. Set Render env vars:
   - `PYTHONPATH=backend`
   - `PARVA_ENABLE_EXPERIMENTAL_API=false`
   - `PARVA_ENV=production`
   - `CORS_ALLOW_ORIGINS=https://dantwoashim.github.io`
4. Deploy static artifacts site via GitHub Pages workflow.
5. Build frontend with production API base:
```bash
cd /Users/rohanbasnet14/Documents/Project_Parva/frontend
VITE_API_BASE=https://<your-render-service>.onrender.com/v3/api npm run build
```
6. Publish frontend build (GitHub Pages / Netlify / Vercel free tier).
7. Run live smoke checks:
```bash
cd /Users/rohanbasnet14/Documents/Project_Parva
python3 scripts/live_smoke.py --base https://<your-render-service>.onrender.com
```

## Health checks
- `GET /health`
- `GET /v3/api/reliability/status` (optional; available when trust routers are enabled)

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
