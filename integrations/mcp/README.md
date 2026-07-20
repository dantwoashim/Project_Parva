---
status: compatibility
last_verified: 2026-07-20
---

# MCP Compatibility Entrypoint

`server.py` forwards to the canonical package in `packages/parva-mcp-server`.
It contains no tool registry, transport implementation, or manifest of its own.

Existing commands remain valid:

```bash
python integrations/mcp/server.py --check
python integrations/mcp/server.py --check-live
python integrations/mcp/server.py --stdio
```

New integrations should launch:

```bash
python -m parva_mcp_server.server --stdio
```
