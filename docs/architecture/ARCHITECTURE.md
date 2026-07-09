# Project Parva Architecture

Project Parva is a modular monolith. The public API is served by FastAPI route
adapters under `backend/app/api` and canonical route packages. Domain behavior
is implemented in services and backend packages, with proof, provenance,
conformance, and source-boundary checks used as first-class runtime concerns.

## Runtime Lanes

| Lane | Purpose | Current boundary |
|---|---|---|
| Stable public runtime | BS/AD conversion, validation, month metadata, fiscal and working-day logic | `backend/app/calendar`, `backend/app/services`, public `/v3/api/*` routes |
| Public preview | Panchanga, muhurta, kundali, agent/proof and trust surfaces | Public or preview routes guarded by route maturity metadata |
| Research | Future-BS and model-risk work that must not publish official future dates | `backend/app/research/future_bs`, compatibility import path `app.future_bs` |
| Experimental | Temporal computing and internal proof experiments that still need import cleanup | `backend/app/experimental` reserved lane, historical packages retained until safe |
| Platform | Bootstrap, settings, middleware, storage, cache, security, billing, deployment support | `backend/app/bootstrap`, `backend/app/storage`, `backend/app/infrastructure`, related packages |

## Public API Rule

`/v3/api/*` is the stable public API contract. Older `/api/*` surfaces are
compatibility aliases. Experimental API tracks must stay disabled by default
unless explicitly enabled by configuration.

## Import Rule

Routes should be thin adapters. They may parse request parameters, call a
service or use-case, and return a presenter/result. Services must not import
route modules. Stable public routes must not import research-private modules.

## Research Boundary

Future-BS work lives under `app.research.future_bs`. The historical
`app.future_bs` namespace remains as a compatibility shim for existing tests,
scripts, and deployment surfaces.

Every future-BS output remains non-official:

```text
publication_status = computed_prediction_not_official
```

## Artifact Boundary

Source archives and generated artifacts must be explicit. Tracked source
archives require checksum metadata. Generated reports should either have a
documented regeneration command or live outside tracked source.
