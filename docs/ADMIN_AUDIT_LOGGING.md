---
status: public-beta
tier: 1
lane: core
last_verified: 2026-05-14
owner: platform-team
---

# Admin Audit Logging

Admin and mutation audit records are part of the production security boundary.
They are not a debugging convenience.

## Billing Audit Records

Billing state changes write persistent rows to `billing_audit_events`.

Covered actions:

- checkout verification
- API-key creation
- API-key revocation
- invoice manual mark-paid
- subscription extension

Each row includes:

- action
- actor principal
- route
- object type and object ID
- before/after SHA-256 hashes where applicable
- request ID
- source IP/context
- scrubbed metadata
- timestamp

Full API-key secrets are never included. Provider references and raw provider
payloads are scrubbed from metadata.

## Provenance And Trust Mutation Audit Records

Provenance write routes are admin-only through the central route access policy.
Mutation endpoints emit persistent JSONL entries through
`backend/app/security/audit.py`.

Covered actions:

- provenance snapshot creation
- transparency log append
- transparency anchor record

Each entry includes actor/context, route, action, object ID, before/after state
hashes where available, request ID, timestamp, source IP/context, and scrubbed
metadata. The default runtime log directory is data/security_audit and the
filename is `admin_mutations.jsonl`;
`PARVA_SECURITY_AUDIT_LOG` can override it for deployment storage.

## Operational Requirement

Production deployments should place the audit log on durable storage or route it
to a log backend with retention and access controls. Losing audit rows is a
security incident for admin/provenance/billing mutation workflows.
