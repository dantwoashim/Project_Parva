---
status: public-beta
tier: 1
lane: core
last_verified: 2026-05-14
owner: platform-team
---

# Agent Safety

The agent layer is an orchestration layer. Deterministic Parva services are the source of truth.

Forbidden behavior:

- inventing dates
- marking unsupported claims as verified
- treating research data as official
- approving legal, payroll, banking, or fiscal-sensitive actions without review gates
- executing arbitrary generated code
- exposing private data in public mode
