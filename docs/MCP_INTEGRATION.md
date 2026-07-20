---
status: stable
tier: 1
lane: dx
last_verified: 2026-07-20
owner: dx-team
---

# MCP Integration

The canonical MCP implementation lives in `packages/parva-mcp-server`. It uses
the official MCP Python SDK and stdio transport. The repository-root package
only extends the source path for local execution, and `integrations/mcp/server.py`
is a compatibility entrypoint. Both resolve to the packaged server.

All nine MCP tools execute through:

```text
POST /v3/api/agent/run-tool
```

The adapter maps each MCP tool to one allowlisted `parva.*` agent tool. Calendar,
festival, compliance, fiscal, panchanga, and claim logic stays in Project Parva's
service layer.

Run locally:

```bash
python -m pip install -e "packages/parva-mcp-server[test]"
python -m parva_mcp_server.server --check
python -m parva_mcp_server.server --check-live
python -m parva_mcp_server.server --stdio
```

`--check` validates schemas, the manifest, the origin, and execution policy
without making a network request. `--check-live` also performs a conversion
through the configured API.

Verification:

```bash
python -m pytest packages/parva-mcp-server/tests -q
python scripts/release/check_mcp_registry_metadata.py
python -m build packages/parva-mcp-server
```

The package is prepared for registry submission. Registry acceptance, listing,
endorsement, and certification require separate external evidence.
