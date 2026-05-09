# Render Public Demo Deployment

This is the lightweight public backend profile for outreach and demos while the
Cloud Run deployment is paused.

## Public Surface

The Render profile uses:

```text
PARVA_ROUTE_PROFILE=public_demo
PARVA_ENABLE_EXPERIMENTAL_API=false
PARVA_SHOW_PRIVATE_SCHEMA=false
```

Only these API paths are intentionally exposed:

- `GET /v3/api/calendar/today`
- `GET /v3/api/calendar/convert`
- `POST /v3/api/calendar/bs-to-gregorian`
- `GET /v3/api/calendar/panchanga`
- `GET /v4/api/future-bs/capabilities`

Private future-BS prediction, export, backtest, model-run, loan-impact, Excel
compare, and sensitive vector routes are not registered in this profile.

## Render Blueprint

The repo includes `render.yaml` for a free web service:

```bash
uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT
```

Render injects `$PORT`; the service must bind to it.

## Required Environment

The blueprint sets:

```text
PARVA_ROUTE_PROFILE=public_demo
PARVA_ENABLE_EXPERIMENTAL_API=false
PARVA_ENV=public
PARVA_SOURCE_URL=https://github.com/dantwoashim/Project_Parva
PARVA_RATE_LIMIT_BACKEND=memory
PARVA_SERVE_FRONTEND=false
PARVA_REQUIRE_PRECOMPUTED=false
CORS_ALLOW_ORIGINS=https://dantwoashim.github.io
```

## Static Docs Mirror

The static Swagger mirror lives in:

```text
docs/api-docs/index.html
docs/api-docs/openapi.json
```

Regenerate it with:

```bash
python scripts/release/generate_public_demo_openapi.py
```

The generated schema points Swagger UI at:

```text
https://project-parva-public-demo.onrender.com
```

For GitHub Pages, publish from the `docs/` folder. The expected mirror path is:

```text
https://dantwoashim.github.io/Project_Parva/api-docs/
```

## Verification

Run:

```bash
python scripts/release/check_render_blueprint.py
python scripts/release/generate_public_demo_openapi.py
python -m pytest tests/integration/test_future_bs_routes.py -q
```
