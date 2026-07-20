# Parva MCP Server

`parva-mcp-server` is the read-only Model Context Protocol server for Project
Parva. It exposes nine Nepali temporal tools over stdio and executes every tool
through one public boundary:

```text
MCP client
  -> parva-mcp-server
  -> POST /v3/api/agent/run-tool
  -> Project Parva temporal services
```

The server uses the official MCP Python SDK. Tool calls return live structured
results, including the source, confidence, evidence, claim boundary, and human
review status supplied by Project Parva.

## Install

Python 3.11 is required. Install from a repository checkout:

```bash
python -m pip install -e "packages/parva-mcp-server[test]"
```

The distribution name is `parva-mcp-server`. Availability from a package
registry requires a separately verified publication record.

## Configure

The default API origin is `https://api.prabinghimire1.com.np`. Override it for
a self-hosted deployment:

```text
PARVA_PUBLIC_ORIGIN=https://parva.example.com
```

Optional settings:

- `PARVA_HTTP_TIMEOUT_SECONDS`: request timeout from 1 to 120 seconds; default 30.
- `PARVA_MAX_RESPONSE_BYTES`: response limit from 1 KiB to 8 MiB; default 2 MiB.
- `PARVA_API_TOKEN`: bearer token for a protected self-hosted API.

Plain HTTP origins are accepted only for `localhost`, `127.0.0.1`, and `::1`.
Redirects are blocked.

Desktop client configuration:

```json
{
  "mcpServers": {
    "project-parva": {
      "command": "python",
      "args": ["-m", "parva_mcp_server.server", "--stdio"],
      "env": {
        "PARVA_PUBLIC_ORIGIN": "https://api.prabinghimire1.com.np"
      }
    }
  }
}
```

## Tools

- `convert_bs_to_ad`
- `convert_ad_to_bs`
- `get_nepali_today`
- `check_holiday`
- `check_working_day`
- `get_fiscal_year`
- `get_festival_date`
- `get_panchanga_summary`
- `check_temporal_claim`

Each tool has a closed JSON Schema with required fields, types, limits, date
formats, and parameter descriptions. Invalid arguments are returned as MCP tool
errors before an HTTP request is sent.

## Resources

- `parva://capabilities`
- `parva://route-maturity`
- `parva://source-policy`
- `parva://supported-ranges`
- `parva://known-limitations`
- `parva://benchmark-summary`

Capabilities and benchmark metadata are read from the live agent gateway. The
benchmark resource therefore follows the generated benchmark artifact instead
of embedding a score in package source.

## Commands

Run the server:

```bash
parva-mcp-server --stdio
```

Check local configuration without a network request:

```bash
parva-mcp-server --check
```

Check configuration and execute a live conversion:

```bash
parva-mcp-server --check-live
```

Print the deterministic descriptor:

```bash
parva-mcp-server --manifest
```

## Error Model

Protocol and schema handling is owned by the official MCP SDK. Project Parva
execution failures use MCP `CallToolResult` with `isError: true` and a structured
error code. Timeouts, network failures, HTTP errors, oversized responses, and
invalid JSON are bounded and sanitized. Standard output contains MCP messages
only.

## Security Boundary

The server cannot execute shell commands, write files, select arbitrary URLs,
or call arbitrary API routes. Every operation maps to the fixed public agent
gateway. Private Future-BS research, admin, billing, key, webhook, and trust
mutation routes stay outside the manifest.

Project Parva is decision support. Government publications and institutional
policy remain authoritative for official, legal, banking, payroll, tax, and
religious decisions.

## Verify

```bash
python -m pytest packages/parva-mcp-server/tests -q
python scripts/release/check_mcp_registry_metadata.py
python -m build packages/parva-mcp-server
```

The test suite launches the server through the official MCP client and checks
initialization, ping, typed tool discovery, live gateway calls, resources,
prompts, schema failures, and sanitized API errors.
