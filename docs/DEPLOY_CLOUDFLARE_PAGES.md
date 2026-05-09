# Deploy on Cloudflare Pages

Use Cloudflare Pages for the static frontend only. The backend API should run separately on Render, Cloud Run, or another ASGI/container host.

## What this repo provides

- a Vite frontend under `frontend/`
- `frontend/public/_redirects` for SPA routing on Pages
- `VITE_API_BASE_URL` support for an absolute API hostname

## Recommended Pages project settings

- Framework preset: `Vite`
- Root directory: `frontend`
- Build command: `npm ci && npm run build`
- Build output directory: `dist`

## Environment variables

Set at least:

- `NODE_VERSION=20`
- `VITE_API_BASE_URL=https://api.prabinghimire1.com.np`

Optional:

- `VITE_API_BASE=https://api.prabinghimire1.com.np/v3/api` for older path-based builds
- `VITE_API_TIMEOUT_MS=10000`

## Preview deployments

Preview deploys are useful for UI validation, but the backend currently expects explicit CORS origins. If your backend only allows the production domain, preview Pages URLs may not be able to call the live API.

The simplest first cut is:

- production Pages domain talks to production API
- preview Pages builds are used for frontend-only validation unless backend CORS is expanded deliberately

## Custom domains

For a typical production layout:

- apex domain: `example.com`
- redirect `www.example.com` to the apex domain

After the domain is attached, confirm:

- direct navigation to deep routes works
- API requests reach the configured `VITE_API_BASE_URL`
- static embed and developer pages under `frontend/public/` still resolve
