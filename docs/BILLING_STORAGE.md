---
status: stable
tier: 1
lane: operations
last_verified: 2026-05-14
owner: platform-team
---

# Billing Storage

The billing store supports SQLite for local/test/development and Postgres for
production/staging deployments.

## Dialects

- `sqlite:///:memory:` and `sqlite:///path` are accepted for local/test/dev.
- `postgres://` and `postgresql://` are accepted for production/staging.
- Unsupported schemes are rejected by `parse_database_url`.

## Schema And Migrations

Migrations are versioned in `backend/app/billing/migrations.py`.

Version 1 installs the foundation tables:

- customers
- plans
- subscriptions
- API keys
- usage events
- usage counters
- payments
- invoices
- webhook subscriptions

Version 2 installs the billing audit table and hot-path indexes. New databases
receive all tables and indexes; older databases that already applied version 1
receive the version 2 additive migration.

## Hot-Path Indexes

- `idx_api_keys_prefix_active`
- `idx_api_keys_customer`
- `idx_subscriptions_customer_status`
- `idx_usage_counters_subject_period`
- `idx_usage_events_subject`
- `idx_usage_events_created`
- `idx_invoices_customer_status`
- `idx_invoices_provider_payment`
- `idx_payments_reference`
- `idx_billing_audit_object`
- `idx_billing_audit_actor`

## Audit Table

`billing_audit_events` records action, actor, route, object type, object ID,
before/after hashes, request ID, source context, scrubbed metadata JSON, and
timestamp.

## Production Rule

Do not run production billing on SQLite. Production/staging validation rejects
SQLite when `PARVA_BILLING_ENABLED=true`.
