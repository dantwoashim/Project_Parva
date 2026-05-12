# API Reference v3

Project Parva v3 APIs are designed to run in two deployment profiles:

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

## API host

The public frontend is hosted on Cloudflare Pages. The public backend API is hosted on Render.

Production URLs:

```text
https://prabinghimire1.com.np
https://api.prabinghimire1.com.np
```

## Canonical route families

The canonical route inventory is generated from the FastAPI app and checked in `docs/ROUTE_ACCESS.md`.

Current v3 route families:

- `admin`
- `billing`
- `cache`
- `calendar`
- `engine`
- `enterprise`
- `explain`
- `feeds`
- `festivals`
- `forecast`
- `glossary`
- `integrations`
- `keys`
- `kundali`
- `me`
- `muhurta`
- `observances`
- `personal`
- `places`
- `policy`
- `provenance`
- `public`
- `reliability`
- `resolve`
- `spec`
- `temples`
- `temporal`
- `webhooks`

Route presence in this reference does not mean every route is available on the lightweight public demo. Public and private deployment boundaries are documented in `docs/PUBLIC_API_BOUNDARY.md`.
