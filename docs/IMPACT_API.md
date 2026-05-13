# Impact API

Public preview endpoints:

- `GET /v3/api/impact/capabilities`
- `POST /v3/api/impact/diff-releases`
- `POST /v3/api/impact/simulate-change-set`
- `POST /v3/api/impact/simulate-release-diff`
- `GET /v3/api/impact/reason-codes`
- `GET /v3/api/impact/recommended-actions`
- `GET /v3/api/impact/event-schema`

Impact output is decision support and uses the claim boundary `impact_simulation_not_legal_authority`.

Use `include_fixture: true` only for public demo and conformance scenarios.
