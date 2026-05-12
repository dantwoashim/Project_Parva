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
PARVA_ENABLE_EXPERIMENTAL_API=false
PARVA_SHOW_PRIVATE_SCHEMA=false
PARVA_SOURCE_URL=https://github.com/dantwoashim/Project_Parva
PARVA_CORS_ORIGINS=https://prabinghimire1.com.np,https://www.prabinghimire1.com.np,https://project-parva.pages.dev
```

If the backend uses `CORS_ALLOW_ORIGINS` instead of `PARVA_CORS_ORIGINS` in a specific deployment profile, use the same comma-separated origin list.

## Private deployment

Private deployments may enable broader route profiles, private schema visibility, or experimental future-BS workflows only with explicit operator configuration.

Recommended private controls:

- keep production and public demo configuration separate
- require admin tokens for private or experimental routes
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
