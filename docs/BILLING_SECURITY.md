---
status: stable
tier: 1
lane: operations
last_verified: 2026-05-14
owner: platform-team
---

# Billing Security

Billing is security-sensitive because it creates API keys, tracks quotas, and
changes commercial access.

## API Keys

- New keys are generated once and returned only at creation time.
- Stored records keep `key_prefix` for lookup and a versioned
  `pbkdf2_sha256` secret hash.
- Each new hash uses a random per-key salt and deployment pepper.
- Verification uses constant-time comparison.
- Legacy SHA-256 hashes remain verify-only for compatibility; new writes do not
  use the legacy format.
- Production and staging billing reject the local default
  `PARVA_API_KEY_PEPPER`.

## Mutation Controls

- Production checkout verification requires admin confirmation.
- Admin invoice mark-paid, subscription extension, and API-key revocation write
  structured audit logs.
- API-key self-revocation is allowed only for the same key principal; other key
  revocation requires admin.
- Manual payment activation and API-key issuance are idempotent: a repeated key
  creation request for the same active subscription returns the existing key
  metadata without revealing the full secret again.

## Storage Requirements

- Production and staging billing require Postgres.
- SQLite billing storage is for local/test/development only.
- SQL uses parameterized placeholders through `BillingStore.param()`.
- Hot paths have indexes for key prefix, customer/subscription lookup, usage
  counters, usage timestamps, invoice status, provider payment lookup, and audit
  event lookup.

## Data Minimization

Billing audit metadata is scrubbed before persistence. Full API keys, raw
provider payloads, emails, phone numbers, names, provider references, and account
identifiers must not appear in audit metadata.
