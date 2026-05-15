# AI Tooling Boundary

## Included

`packages/parva-ai-tools` exposes safe wrappers for stable public capabilities:

- convert BS to AD
- convert AD to BS
- get today's Nepali date
- check holiday
- get working-day status
- get fiscal year
- get festival date
- get Panchanga summary
- check temporal claim

Each normalized response carries:

- answer
- source tier
- confidence
- supported range
- claim boundary
- review required
- not authority

## Excluded

The AI tooling does not expose exact unsupported Future-BS prediction, loan-impact prediction, private source audit, research backtest, calendar stress tests, mutation/admin/trust routes, billing/admin routes, or private route tokens.

## MCP

The MCP package is a thin optional read-only adapter over the same public-safe capabilities. It is not the core runtime and does not create authority.
