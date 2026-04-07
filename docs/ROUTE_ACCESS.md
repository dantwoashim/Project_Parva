# Route Access

Project Parva uses a truthful public-access model for the normal `v3` surface.

## Summary

| Route family | Access | Notes |
| --- | --- | --- |
| `/v3/api/calendar/*` | Public | Canonical read and conversion routes |
| `/v3/api/festivals/*` | Public | Public read routes with trust metadata |
| `/v3/api/feeds/*` and `/v3/api/integrations/feeds/*` | Public | Feed and integration helpers |
| `/v3/api/personal/*` | Public compute | Location-sensitive compute surface; clients should treat results as request-sensitive |
| `/v3/api/muhurta/*` | Public compute | Public by default, not an account-only feature |
| `/v3/api/kundali/*` | Public compute | Public by default, informational/tradition-scoped |
| `/v3/api/temporal/*` | Public compute | Public by default |
| `/v3/api/reliability/*`, `/v3/api/provenance/*`, `/v3/api/policy` | Public | Trust, provenance, and policy inspection |
| `/api/*` | Public legacy alias | Compatibility only |
| `/v2`, `/v4`, `/v5` | Experimental | Disabled by default |
| Admin-only or mutation routes | Protected | Require scoped API key or admin bearer token |

## Important clarifications

- Public compute does not mean Parva stores private account state for you.
- Experimental tracks are not independent long-term contracts.
- Route access is also exposed in machine-readable form at `/v3/api/policy`.
