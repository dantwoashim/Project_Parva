---
status: stable
tier: 1
lane: operations
last_verified: 2026-05-14
owner: platform-team
---

# Deployment

Project Parva is designed to run in two deployment profiles:

1. A public demo profile for safe API evaluation.
2. A private or full deployment profile for organizations that need controlled calendar validation, internal audit workflows, or sensitive future-BS research surfaces.

The current public deployment uses:

| Layer | Platform | URL |
|---|---|---|
| Frontend | Cloudflare Pages | https://prabinghimire1.com.np |
| Backend API | Render | https://api.prabinghimire1.com.np |
| Source code | GitHub | https://github.com/dantwoashim/Project_Parva |

The public backend is intentionally narrower than a full private deployment. It exposes stable public calendar and methodology surfaces, while private or experimental future-BS workflows stay disabled by default.

## Public deployment boundary

The public API demo is for technical evaluation, documentation, and public-safe calendar functionality.

Public surfaces may include:

- health/status endpoints
- BS/AD conversion
- current Nepali date
- BS date validation
- fiscal-year helpers where enabled
- public panchanga endpoints where enabled
- public festival endpoints where enabled
- future-BS capabilities summary

Private or experimental surfaces must stay disabled by default on the public deployment:

- direct future BS month-length prediction
- future range prediction
- CSV/XLSX future exports
- model runs
- backtests
- residual analysis
- client sheet comparison
- loan-impact simulation
- corrected future values
- private audit workflows

Future-BS research outputs are treated as:

`computed_prediction_not_official`

Project Parva is not an official government calendar publication, legal authority, tax authority, banking-contract authority, or replacement for official Nepali calendar publication.

## Frontend deployment

The frontend is hosted on Cloudflare Pages.

Production frontend URL:

```text
https://prabinghimire1.com.np
```

Set this environment variable in Cloudflare Pages:

```text
VITE_API_BASE=https://api.prabinghimire1.com.np/v3/api
```

The frontend code should use `VITE_API_BASE` as the single public API base. Do not use legacy Cloud Run URLs or alternate API-base variables in public builds.

## Backend deployment

The public backend API is hosted on Render.

Production API URL:

```text
https://api.prabinghimire1.com.np
```

Render start command:

```bash
uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT
```

Public-safe backend environment:

```text
PARVA_ENV=public
PARVA_ROUTE_PROFILE=developer_preview
PARVA_ENABLE_EXPERIMENTAL_API=false
PARVA_SHOW_PRIVATE_SCHEMA=false
PARVA_ALLOW_PUBLIC_UNVERIFIED_FUTURE_CONVERSION=false
PARVA_SOURCE_URL=https://github.com/dantwoashim/Project_Parva
PARVA_RATE_LIMIT_BACKEND=memory
PARVA_REQUIRE_PRECOMPUTED=false
PARVA_PREWARM_HOTSET=true
PARVA_CORS_ORIGINS=https://prabinghimire1.com.np,https://www.prabinghimire1.com.np,https://project-parva.pages.dev
```

The backend accepts either `CORS_ALLOW_ORIGINS` or `PARVA_CORS_ORIGINS`. Use the same comma-separated origin list.

Do not set the public Render demo to `PARVA_ENV=production` unless Redis-backed rate limiting and all production checks are configured. `production` is the strict private or hardened deployment profile. The public demo profile is `public`.

The repository Docker images also default to the `public` profile so a smoke
container does not claim hardened production posture without injected Redis and
source metadata. Operators who need a strict production container should set at
least `PARVA_ENV=production`, `PARVA_SOURCE_URL`, `PARVA_RATE_LIMIT_BACKEND=redis`,
and `PARVA_REDIS_URL` at deployment time.

## Rate limits, metrics, and security headers

The public demo may use the in-process rate limiter because it is a lightweight
evaluation service. Production-like deployments must use:

```text
PARVA_RATE_LIMIT_BACKEND=redis
PARVA_REDIS_URL=rediss://...
```

In-process metrics are process-local. Treat them as local health telemetry, not
as global multi-worker business metrics.

The backend sets conservative API security headers, including:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: no-referrer`
- `Content-Security-Policy: default-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'self'`

Cloudflare Pages should also define its own frontend CSP if custom scripts,
analytics, or embedded widgets are added.

## Static embeds

Static embed pages under `frontend/public/embed/` can run from a static host and
call the public API directly. They accept either:

```text
?api_base=https://api.prabinghimire1.com.np/v3/api
```

or a host-provided `data-api-base` value on the document body. If no value is
provided, they default to the public Render API base.

## Private deployment

Private deployments may enable broader route profiles, private schema visibility, or experimental future-BS workflows only with explicit operator configuration.

Recommended private controls:

- keep production and public demo configuration separate
- require admin tokens for private or experimental routes
- decide and document whether unverified future BS-to-AD conversion is allowed before setting `PARVA_ALLOW_PUBLIC_UNVERIFIED_FUTURE_CONVERSION=true`
- keep generated future-BS artifacts outside public source control
- preserve `computed_prediction_not_official` on future-BS research outputs
- validate any organizational update policy against official publications before production use

## Health checks

Use these endpoints where available:

```text
/health/live
/health/ready
```

The public API demo may sleep when idle. First requests can take a few seconds while the instance wakes up.

## Route profiles

Route profiles keep public deployment, developer preview, enterprise preview,
and local development behavior explicit.

| Profile | Purpose |
|---|---|
| `minimal_public` | Health, public calendar demo routes, and safe capability summaries |
| `public_demo` | Compatibility alias for the narrow public demo profile |
| `public_reference` | Calendar, festivals, feeds, panchanga-style public surfaces, trust capabilities, and protocol capabilities |
| `developer_preview` | Public reference routes plus trust, TimeGraph, RuleLang, impact, agent, and protocol preview routes |
| `enterprise_preview` | Developer preview plus billing and monetization routes |
| `full_dev` | Full local development route set |
| `full` | Legacy full route profile for local or controlled deployments |

The Render public service currently uses `developer_preview` because the
frontend and public docs advertise trust, protocol, impact, and agent
capability surfaces. Private future-BS prediction, export, backtest, model-run,
and corrected-value routes still require explicit experimental flags and are not
part of the public profile.

## Python runner

Public verification is Python 3.11-only. The Makefile accepts an explicit
runner:

```bash
make verify-public PYTHON=/path/to/python3.11
```

Scripts that need to re-execute Python also honor:

```text
PARVA_PYTHON=/path/to/python3.11
```

On Windows, the Python launcher is acceptable for manual use. CI and
cross-platform scripts should prefer `python` from a configured Python 3.11
environment or `PARVA_PYTHON`.
