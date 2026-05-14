---
status: public-beta
tier: 2
lane: dx
last_verified: 2026-05-14
owner: dx-team
---

# Parva MCP Integration

This directory contains a minimal Model Context Protocol integration scaffold for
Project Parva's agent-safe temporal tools.

## Files

- `parva_mcp_manifest.json`: local tool manifest for MCP host wiring.
- `server.py`: stdio JSON-RPC scaffold for safe public tools.

The integration is intentionally bounded. It exposes only public, deterministic,
agent-safe operations and must preserve human-review behavior for payroll,
banking, legal, fiscal, future, private-source, disputed-source, and
official-source-sensitive claims.

## Verification

```bash
python integrations/mcp/server.py --manifest
```
