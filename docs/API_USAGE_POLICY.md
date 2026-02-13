# API Usage Policy (Current + Forward Plan)

## Current (Development Stage)
- No hard rate limiting is enforced.
- Clients should still avoid tight polling loops.
- Cache responses for date-based queries where possible.

## Recommended Client Behavior
- Use `GET /calendar/panchanga` at most once per date/timezone context.
- Prefer batch/range endpoints over many single-day requests.
- Respect `confidence` and `method` fields when displaying results.
- Handle non-200 responses with retry backoff.

## Forward Plan (Production)
- Anonymous quota: soft burst + daily cap.
- API key quota tiers for partners.
- Per-IP abuse throttling.
- Deprecation window: minimum 6 months for contract-breaking changes.

## Versioning
- Use `/v2/api/*` for all new integrations.
- Legacy `/api/*` paths include deprecation headers and planned sunset metadata.
