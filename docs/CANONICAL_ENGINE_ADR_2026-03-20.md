# ADR: Canonical Public Engine

Date: 2026-03-20
Status: Accepted

## Context
Parva accumulated multiple compute paths, legacy calculators, and snapshot metadata that did not clearly identify the runtime actually serving the public API.
This created launch risk in three places:

- public routes could appear interchangeable while exercising different internals
- provenance records exposed hashes without a stable engine identity
- compatibility components could be mistaken for the public source of truth

## Decision
Parva adopts one canonical public runtime identity:

- canonical engine id: `parva-v3-canonical`
- canonical manifest version: `2026-03-20`
- public manifest endpoint: `/api/engine/manifest` and `/v3/api/engine/manifest`

The public engine maps route families to explicit runtime components:

- `calendar_core`
  - `app.calendar.routes`
  - `app.calendar.bikram_sambat`
  - `app.calendar.panchanga`
  - `app.calendar.tithi`
- `festival_rules`
  - `app.rules.service.FestivalRuleService`
  - `app.calendar.calculator_v2`
  - `app.rules.catalog_v4`
- `personal_stack`
  - `app.api.personal_routes`
  - `app.api.muhurta_routes`
  - `app.api.kundali_routes`
  - `app.api.temporal_compass_routes`

Legacy components remain compatibility-only:

- `app.calendar.calculator`
- `app.calendar.festival_rules.json`

## Provenance policy
Snapshot records now expose:

- canonical engine id
- manifest version
- manifest hash
- build SHA
- dependency lock hash
- runtime metadata
- attestation metadata

Parva does not label plain hashes as signatures.
If `PARVA_PROVENANCE_ATTESTATION_KEY` is configured, the system emits `hmac-sha256` attestations.
If no key is configured, the system emits explicit `unsigned` attestations so the trust model remains honest.

## Consequences
Positive:

- public routing, engine identity, and provenance are now aligned
- operators can inspect the serving runtime through one stable manifest
- compatibility code stays available without being presented as the public engine

Tradeoffs:

- build metadata is now stricter and must be maintained in release automation
- downstream tooling that expected `signature` should migrate to `attestation`
- full asymmetric signing is still deferred until a key-management path is in place
