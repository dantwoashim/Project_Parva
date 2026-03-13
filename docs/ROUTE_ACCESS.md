# Route Access Policy

Project Parva ships a narrow public stable profile.

## Public read

- `/api/*` and `/v3/api/*` for calendar conversion, festival explorer,
  feeds, personal panchanga, muhurta, kundali, temporal compass, glossary,
  and other stateless read-only product routes.
- `/health/live`
- `/health/ready`
- `/health/startup`

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
- Webhook management is not shipped in this build.

## Admin only

- Provenance mutation routes
- Experimental write routes
- No webhook routes are available in the shipped launch profile

## Local development credentials

When `PARVA_ENV` is `development`, `dev`, `local`, or `test`, the app exposes
deterministic local-only credentials if none are provided:

- Read key: `parva-dev-read-key`
- Admin bearer token: `parva-dev-admin-token`

These defaults are for local testing only and must not be used in production.
