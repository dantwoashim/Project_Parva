# Architecture Boundaries

This document defines the current ownership boundaries for Parva's backend.

## Canonical Boundaries

- `backend/app/api/*`
  - Thin HTTP adapters only.
  - Parse request params, call one use case/service, return the presenter result.
  - Must not import other route modules.

- `backend/app/calendar/routes.py`
  - Canonical calendar route surface.
  - Uses application services, not route-to-route orchestration.

- `backend/app/festivals/routes.py`
  - Canonical festival route surface.
  - Uses festival use cases + presenters.

- `backend/app/services/*`
  - Application-layer orchestration for calendar, personal, muhurta, compass, timeline, and trust surfaces.
  - Must not import route modules.

- `backend/app/festivals/use_cases.py`
  - Festival-specific application use cases.
  - Owns orchestration, filtering, and route-independent response assembly inputs.

- `backend/app/festivals/presenters.py`
  - Canonical response presenters for festival list/detail/calendar/dispute surfaces.

- `backend/app/storage/*`
  - Persistence abstractions and file-backed adapters.
  - Must remain framework-agnostic.

- `backend/app/infrastructure/*`
  - Low-level operational adapters such as precomputed artifact loading.
  - Must remain framework-agnostic.

## Canonical vs Compatibility Endpoints

- Canonical public beta surfaces live under:
  - `/api/*`
  - `/v3/api/*`

- Compatibility wrappers still exist for:
  - `backend/app/api/calendar_routes.py`
  - `backend/app/api/festival_routes.py`

Those wrappers intentionally re-export the canonical route modules. They should stay tiny and should not accumulate business logic.

## Trust Route Policy

Read-only operational routes are public in the v3 profile:

- `/api/reliability/*`
- `/api/provenance/root`
- `/api/provenance/proof`
- `/api/public-artifacts/*`
- `/api/spec/conformance`

Mutating provenance routes remain admin-only.

## Observability Split

- Product-visible reliability data:
  - `status`
  - public warnings
  - precomputed freshness
  - hotset latency probes

- Telemetry-only data:
  - request counters
  - p95 latency
  - degraded-state counters
  - runtime cache stats/evictions
  - Prometheus exposition

## Contributor Rules

- Do not import `app.services` as a barrel from route modules; import the concrete service/use-case module instead.
- Do not add new route-to-route imports.
- Do not add FastAPI dependencies inside `backend/app/storage/*` or `backend/app/infrastructure/*`.
- New public response metadata should go through presenters/trust helpers instead of ad hoc route assembly.
- If a route is only a compatibility alias, keep it as a wrapper and avoid feature growth there.
