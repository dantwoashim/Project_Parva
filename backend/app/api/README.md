# API Layer

`backend/app/api/` exposes HTTP routes and response serialization only.

Responsibilities:
- Input validation and HTTP error mapping.
- Calling `engine/`, `rules/`, and `sources/` services.
- Returning stable JSON contracts.

No business logic should be implemented directly in route handlers.

Primary routers:
- `calendar_routes.py` → `/api/calendar/*`
- `festival_routes.py` → `/api/festivals/*`
- `forecast_routes.py` → `/api/forecast/*` (long-horizon confidence-decay projections)
- `explain_routes.py` → `/api/explain/*` (deterministic reason traces)
- `observance_routes.py` → `/api/observances/*` (cross-calendar resolver)
- `feed_routes.py` → `/api/feeds/*` (iCal surfaces)
- `webhook_routes.py` → `/api/webhooks/*` (subscriptions + dispatch)
- `cache_routes.py` → `/api/cache/*` (precompute/cache artifacts inspection)
- `reliability_routes.py` → `/api/reliability/*` (SLO status + playbooks)
- `policy_routes.py` → `/api/policy/*` (usage/disclaimer metadata)
