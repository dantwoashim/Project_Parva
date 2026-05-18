---
status: public-preview
audience: agent-tooling
---

# MCP Security Policy

The Parva MCP adapter is read-only by default.

The live `--stdio` server accepts only newline-delimited JSON-RPC requests for
the whitelisted MCP methods: `initialize`, `tools/list`, `tools/call`,
`resources/list`, `resources/read`, `prompts/list`, and `prompts/get`.

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

Resource reads are restricted to whitelisted `parva://` resources. `file://`,
`http://`, relative paths, absolute paths, and unknown schemes are rejected.

Tool descriptors must preserve `claim_boundary`, `review_required`, and the
authority boundary. A model calling Parva may use it as deterministic decision
support, not as official government, legal, tax, banking, payroll, future-date,
or religious authority.

Registry metadata must pass `python scripts/release/check_mcp_registry_metadata.py`
before submission. A passing metadata check only means the local descriptor is
safe to submit; it does not mean registry acceptance or external certification.
