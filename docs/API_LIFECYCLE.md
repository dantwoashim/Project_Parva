# API Lifecycle

Project Parva is `v3`-first.

## Canonical public API

- Primary public surface: `/v3/api/*`
- OpenAPI document: `/v3/openapi.json`
- Interactive docs: `/v3/docs`

All new integrations should target `/v3/api/*`.

## Compatibility surface

Parva still serves `/api/*` as a compatibility alias for the current public product.

Compatibility rules:

1. `/api/*` exists to support older integrations and the current hosted app.
2. New features should land on the canonical implementation first and only be mirrored through the alias where required.
3. Compatibility wrappers must stay thin. They should not accumulate route-specific business logic.
4. Experimental tracks (`/v2`, `/v4`, `/v5`) are not part of the supported public contract.

## Sunset posture

There is no immediate removal date for `/api/*`, but it should be treated as transitional.

Future removal requires all of the following:

1. the hosted app uses `/v3/api/*` everywhere,
2. the SDK defaults to `/v3/api/*`,
3. the route inventory stays clean, and
4. a release note announces the compatibility retirement window.

## Release checks

The release process enforces:

- frozen v3 OpenAPI contract,
- route inventory snapshot,
- compatibility alias coverage,
- clean source archive generation.
