# Parva MCP Server

This package is a thin, optional, read-only MCP stdio server for Project Parva
public temporal capabilities.

It is not the core runtime. It does not call private Future-BS prediction,
private source audit, admin, billing, trust mutation, shell execution, or
filesystem write surfaces.

Resources:

- `parva://capabilities`
- `parva://route-maturity`
- `parva://source-policy`
- `parva://supported-ranges`
- `parva://known-limitations`
- `parva://benchmark-summary`

Tools:

- `convert_bs_to_ad`
- `convert_ad_to_bs`
- `get_nepali_today`
- `check_holiday`
- `check_working_day`
- `get_fiscal_year`
- `get_festival_date`
- `get_panchanga_summary`
- `check_temporal_claim`

Prompts:

- `explain_nepali_date_safely`
- `check_claim_with_sources`
- `plan_schedule_with_review_gates`

Parva MCP is decision support only. It is not official government, legal, tax,
banking, payroll, future-date, or religious authority.

## Commands

`--manifest` prints the safe manifest and exits:

```bash
python -m parva_mcp_server.server --manifest
```

`--check` validates the manifest and public tool surface and exits:

```bash
python -m parva_mcp_server.server --check
```

`--stdio` runs the live newline-delimited JSON-RPC MCP server process used by
Claude Desktop, Codex-style MCP clients, and other stdio launchers:

```bash
python -m parva_mcp_server.server --stdio
```

Example smoke request:

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python -m parva_mcp_server.server --stdio
```

The stdio server does not execute shell commands, write files, expose private
routes, or return exact unsupported Future-BS predictions. Without a configured
API client it returns `manifest_only` tool results containing route, method,
`claim_boundary`, `review_required`, and `not_authority`.
