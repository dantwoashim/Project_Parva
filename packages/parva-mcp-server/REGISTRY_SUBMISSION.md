# MCP Registry Submission Notes

Package name: `parva-mcp-server`

Description: read-only MCP adapter for public-safe Project Parva Nepali
temporal tools.

Status: ready for submission. This repository does not claim registry
acceptance, listing, endorsement, or external certification.

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

## Resources

- `parva://capabilities`
- `parva://route-maturity`
- `parva://source-policy`
- `parva://supported-ranges`
- `parva://known-limitations`
- `parva://benchmark-summary`

## Install And Run

```bash
python -m pip install parva-mcp-server
parva-mcp-server --manifest
parva-mcp-server --check
```

Local repository run:

```bash
python -m parva_mcp_server.server --manifest
python -m parva_mcp_server.server --check
```

## Security Model

- read-only by default
- no shell execution
- no filesystem writes
- no private, research, admin, billing, key, webhook, or trust mutation routes
- no exact unsupported Future-BS predictions
- no public authority claim

Parva MCP is decision support only. It is not government, legal, tax, banking,
payroll, religious, official future-date, registry-endorsed, or certified
authority.

## Example Config

See `examples/claude_desktop_config.example.json`. The example contains no
secrets.
