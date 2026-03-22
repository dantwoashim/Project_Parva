# Route Access Policy

Project Parva ships a narrow public stable profile.

## Public read

- `/api/*` and `/v3/api/*` for calendar conversion, festival explorer,
  feeds, personal panchanga, muhurta, kundali, temporal compass, glossary,
  and other stateless read-only product routes.
- `/health/live`
- `/health/ready`
- `/health/startup`

## Launch-critical product surface

These are the only consumer experiences treated as launch-critical for contract,
QA, and design-polish purposes:

- Today / Temporal Compass
- Personal Panchanga / My Place
- Muhurta / Best Time
- Festival Explorer + Festival Detail
- Kundali / Birth Reading

Other public routes remain available, but they are support or compatibility
surfaces and are not a reason to loosen the launch gate for the five flows
above.

The consumer shell and command search now treat those five journeys as the only
first-class destinations. Support, beta, and deferred pages remain reachable,
but they are deliberately de-emphasized in primary navigation and surfaced with
explicit tier messaging.

## Public route tiers

- Launch-critical: the five consumer flows above on `/v3/api/*` and the `/api/*`
  compatibility alias
- Support/public beta: feeds, glossary, health endpoints, methodology/about
  content, and institutional/public-artifact read surfaces
- Experimental/deferred: `/v2/*`, `/v4/*`, `/v5/*`, mutable provenance routes,
  and other non-launch admin/developer surfaces

## Authenticated read

These routes are disabled in the production public profile by default. When
enabled in local or experimental environments, they require either:

- `X-API-Key` with `commercial.read`, or
- `Authorization: Bearer <admin-token>`

Routes:

- `/api/reliability/*`
- `/api/spec/*`
- `/api/public/*`
- read-only provenance verification routes under `/api/provenance/*`
- the `/v2/*`, `/v4/*`, and `/v5/*` experimental tracks

## Owner-scoped write

- No owner-scoped write routes are part of the launch profile.

## Admin only

- Provenance mutation routes
- Experimental write routes

## Test-only credentials

When running tests, the app exposes deterministic test-only credentials if none
are provided:

- Read key: `parva-test-read-key`
- Admin bearer token: `parva-test-admin-token`

These defaults are for automated/local test runs only and must not be used in
development or production environments.

## Recommended external packaging

- Keep anonymous public `v3` product routes free.
- Gate reliability, conformance, public-artifact, and provenance verification reads behind `commercial.read`.
- Use `PARVA_API_KEYS` to provision external partners instead of exposing admin credentials.
- See `docs/HOSTED_API_ONBOARDING.md`, `docs/PARTNER_ACCESS.md`, and `docs/USAGE_TIERS.md`.
