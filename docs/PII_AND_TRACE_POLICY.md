---
status: public-beta
tier: 1
lane: core
last_verified: 2026-05-14
owner: platform-team
---

# PII And Trace Policy

Project Parva traces, logs, evidence packets, billing audits, RuleLang traces,
and agent explanations must preserve auditability without storing private user
data in public or long-lived artifacts.

## Redacted By Default

The conservative scrubber in `backend/app/security/pii.py` redacts common PII
patterns and denylisted field names:

- names and client names when field names identify them as personal data
- email addresses
- phone numbers, including Nepal mobile formats
- citizenship IDs
- account identifiers
- cooperative member IDs and payroll identifiers when field names identify them
- precise address markers such as ward, tole, street, road, municipality, and
  province fragments
- raw provider payloads and provider references in audit metadata

## Preserved Audit Identifiers

The scrubber allowlists non-PII identifiers that are needed for verification:

- source IDs and evidence IDs
- fact IDs
- trace IDs
- release IDs
- artifact IDs
- dataset and rules hashes
- request IDs
- invoice, subscription, and key IDs

## Persistence Points

- Public `FileTraceStore` traces scrub subject, inputs, outputs, steps, and
  provenance before writing JSON.
- Private traces keep private subject/input redaction and also scrub outputs,
  steps, and provenance.
- Transparency log payloads are scrubbed before hash-chain entry creation.
- Billing audit metadata is scrubbed before database persistence.
- RuleLang traces scrub scalar values and nested field names before returning or
  persisting trace material.

## Review Rule

Do not add new trace/log/evidence persistence that writes request bodies,
provider payloads, customer data, private source text, or agent inputs without
passing the payload through `scrub_structured_trace` or a narrower equivalent.
