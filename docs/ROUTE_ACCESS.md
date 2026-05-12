# Route Access Inventory

This file is the canonical route inventory used by release checks.

It lists current `v3` API routes so documentation drift is visible during tests. Route presence here does not mean every route is part of the lightweight public demo. Public deployment policy is documented in `docs/PUBLIC_API_BOUNDARY.md`.

## Access Notes

- Public demo routes are controlled by deployment profile and environment variables.
- Admin, billing, partner, and internal routes may require authentication or private deployment policy.
- Experimental future-BS prediction and export surfaces remain gated outside the public profile.

## Canonical v3 Routes (152)

### admin

- `POST /v3/api/admin/api-keys/{key_id}/revoke`
- `GET /v3/api/admin/customers`
- `POST /v3/api/admin/invoices/{invoice_id}/mark-paid`
- `GET /v3/api/admin/subscriptions`
- `POST /v3/api/admin/subscriptions/{subscription_id}/extend`
- `GET /v3/api/admin/usage/anomalies`

### billing

- `POST /v3/api/billing/checkout`
- `GET /v3/api/billing/checkout/{checkout_id}`
- `POST /v3/api/billing/checkout/{checkout_id}/verify`
- `GET /v3/api/billing/plans`

### cache

- `GET /v3/api/cache/festivals/{year}`
- `GET /v3/api/cache/panchanga/{year}/{month}/{day}`
- `GET /v3/api/cache/stats`

### calendar

- `POST /v3/api/calendar/bs-to-gregorian`
- `GET /v3/api/calendar/convert`
- `GET /v3/api/calendar/convert/compare`
- `GET /v3/api/calendar/dual-month`
- `GET /v3/api/calendar/festivals/calculate/{festival_id}`
- `GET /v3/api/calendar/festivals/upcoming`
- `GET /v3/api/calendar/panchanga`
- `GET /v3/api/calendar/panchanga/proof-capsule`
- `GET /v3/api/calendar/panchanga/range`
- `GET /v3/api/calendar/sankranti/{year}`
- `GET /v3/api/calendar/tithi`
- `GET /v3/api/calendar/tithi/proof-capsule`
- `GET /v3/api/calendar/today`
- `GET /v3/api/calendar/today/proof-capsule`

### engine

- `GET /v3/api/engine/calendars`
- `GET /v3/api/engine/config`
- `GET /v3/api/engine/convert`
- `GET /v3/api/engine/health`
- `GET /v3/api/engine/manifest`
- `GET /v3/api/engine/observance-calculate`
- `GET /v3/api/engine/observance-plugins`
- `GET /v3/api/engine/observances`
- `GET /v3/api/engine/plugins/quality`

### enterprise

- `GET /v3/api/enterprise/bs-months/{bs_year}`
- `POST /v3/api/enterprise/bulk-convert`
- `POST /v3/api/enterprise/business-days`
- `GET /v3/api/enterprise/capabilities`
- `GET /v3/api/enterprise/fiscal-year/{bs_year}`
- `POST /v3/api/enterprise/validate`

### explain

- `GET /v3/api/explain`
- `GET /v3/api/explain/`
- `GET /v3/api/explain/{trace_id}`

### feeds

- `GET /v3/api/feeds/all.ics`
- `GET /v3/api/feeds/custom.ics`
- `GET /v3/api/feeds/ical`
- `GET /v3/api/feeds/integrations/catalog`
- `GET /v3/api/feeds/integrations/custom-plan`
- `GET /v3/api/feeds/national.ics`
- `GET /v3/api/feeds/newari.ics`
- `GET /v3/api/feeds/next`

### festivals

- `GET /v3/api/festivals`
- `GET /v3/api/festivals/calendar/{year}/{month}`
- `GET /v3/api/festivals/coverage`
- `GET /v3/api/festivals/coverage/scoreboard`
- `GET /v3/api/festivals/disputes`
- `GET /v3/api/festivals/on-date/{target_date}`
- `GET /v3/api/festivals/timeline`
- `GET /v3/api/festivals/upcoming`
- `GET /v3/api/festivals/{festival_id}`
- `GET /v3/api/festivals/{festival_id}/dates`
- `GET /v3/api/festivals/{festival_id}/explain`
- `GET /v3/api/festivals/{festival_id}/proof-capsule`
- `GET /v3/api/festivals/{festival_id}/variants`

### forecast

- `GET /v3/api/forecast/error-curve`
- `GET /v3/api/forecast/festivals`

### glossary

- `GET /v3/api/glossary`

### integrations

- `GET /v3/api/integrations/feeds/all.ics`
- `GET /v3/api/integrations/feeds/catalog`
- `GET /v3/api/integrations/feeds/custom-plan`
- `GET /v3/api/integrations/feeds/custom.ics`
- `GET /v3/api/integrations/feeds/national.ics`
- `GET /v3/api/integrations/feeds/newari.ics`
- `GET /v3/api/integrations/feeds/next`

### keys

- `POST /v3/api/keys`
- `DELETE /v3/api/keys/{key_id}`

### kundali

- `GET /v3/api/kundali`
- `POST /v3/api/kundali`
- `GET /v3/api/kundali/graph`
- `POST /v3/api/kundali/graph`
- `GET /v3/api/kundali/lagna`
- `POST /v3/api/kundali/lagna`

### me

- `GET /v3/api/me/usage`

### muhurta

- `GET /v3/api/muhurta`
- `POST /v3/api/muhurta`
- `GET /v3/api/muhurta/auspicious`
- `POST /v3/api/muhurta/auspicious`
- `GET /v3/api/muhurta/calendar`
- `GET /v3/api/muhurta/heatmap`
- `POST /v3/api/muhurta/heatmap`
- `GET /v3/api/muhurta/rahu-kalam`
- `POST /v3/api/muhurta/rahu-kalam`

### observances

- `GET /v3/api/observances`
- `GET /v3/api/observances/conflicts`
- `GET /v3/api/observances/next`
- `GET /v3/api/observances/stream`
- `GET /v3/api/observances/today`

### personal

- `GET /v3/api/personal/context`
- `POST /v3/api/personal/context`
- `GET /v3/api/personal/context/proof-capsule`
- `POST /v3/api/personal/context/proof-capsule`
- `GET /v3/api/personal/panchanga`
- `POST /v3/api/personal/panchanga`
- `GET /v3/api/personal/panchanga/proof-capsule`
- `POST /v3/api/personal/panchanga/proof-capsule`

### places

- `GET /v3/api/places/search`

### policy

- `GET /v3/api/policy`
- `GET /v3/api/policy/`

### provenance

- `GET /v3/api/provenance/batch-verify`
- `GET /v3/api/provenance/dashboard`
- `GET /v3/api/provenance/proof`
- `GET /v3/api/provenance/root`
- `POST /v3/api/provenance/snapshot/create`
- `GET /v3/api/provenance/snapshot/{snapshot_id}/verify`
- `GET /v3/api/provenance/transparency/anchor/prepare`
- `POST /v3/api/provenance/transparency/anchor/record`
- `GET /v3/api/provenance/transparency/anchors`
- `POST /v3/api/provenance/transparency/append`
- `GET /v3/api/provenance/transparency/audit`
- `GET /v3/api/provenance/transparency/log`
- `GET /v3/api/provenance/transparency/replay`
- `GET /v3/api/provenance/verify/trace/{trace_id}`
- `GET /v3/api/provenance/verify/{festival_id}`

### public

- `GET /v3/api/public/artifacts/boundary-suite`
- `GET /v3/api/public/artifacts/dashboard`
- `GET /v3/api/public/artifacts/differential`
- `GET /v3/api/public/artifacts/manifest`
- `GET /v3/api/public/artifacts/precomputed/{filename}`
- `GET /v3/api/public/artifacts/source-review-queue`

### reliability

- `GET /v3/api/reliability/benchmark-manifest`
- `GET /v3/api/reliability/boundary-suite`
- `GET /v3/api/reliability/differential-manifest`
- `GET /v3/api/reliability/metrics`
- `GET /v3/api/reliability/metrics.prom`
- `GET /v3/api/reliability/playbooks`
- `GET /v3/api/reliability/slos`
- `GET /v3/api/reliability/source-review-queue`
- `GET /v3/api/reliability/status`

### resolve

- `GET /v3/api/resolve`

### spec

- `GET /v3/api/spec/conformance`

### temples

- `GET /v3/api/temples`
- `GET /v3/api/temples/for-festival/{festival_id}`
- `GET /v3/api/temples/{temple_id}`
- `GET /v3/api/temples/{temple_id}/festivals`

### temporal

- `GET /v3/api/temporal/compass`
- `POST /v3/api/temporal/compass`
- `GET /v3/api/temporal/compass/proof-capsule`
- `POST /v3/api/temporal/compass/proof-capsule`

### webhooks

- `GET /v3/api/webhooks`
- `POST /v3/api/webhooks`
