---
status: public-preview
audience: ai-tooling
---

# MCP Security Policy

The Parva MCP adapter is read-only by default.

Hard rules:

- no shell execution,
- no filesystem writes,
- no private Future-BS routes,
- no admin routes,
- no billing routes,
- no key or webhook routes,
- no trust mutation routes,
- no exact unsupported Future-BS predictions,
- no private route token leakage,
- no authority claims.

Tool descriptors must preserve `claim_boundary`, `review_required`, and the
authority boundary. A model calling Parva may use it as deterministic decision
support, not as official government, legal, tax, banking, payroll, future-date,
or religious authority.

Registry metadata must pass `python scripts/release/check_mcp_registry_metadata.py`
before submission. A passing metadata check only means the local descriptor is
safe to submit; it does not mean registry acceptance or external certification.
