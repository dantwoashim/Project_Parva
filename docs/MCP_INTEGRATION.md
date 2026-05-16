---
status: public-preview
audience: ai-tooling
---

# MCP Integration

Parva MCP is optional and thin. It sits after the public tool-wrapper layer and
exposes only read-only public-safe capabilities.

The package lives in `packages/parva-mcp-server`. Its manifest exposes public
resources for capabilities, route maturity, source policy, supported ranges,
known limitations, and benchmark summary. The tool list mirrors the safe public
tool surface: conversion, today's Nepali date, holiday/working-day support,
fiscal year, festival date, panchanga summary, and temporal claim checking.

Distribution metadata lives in `packages/parva-mcp-server/mcp-server.json` and
can be checked with:

```bash
python scripts/release/check_mcp_registry_metadata.py
```

The package is ready for submission. It is not accepted, listed, endorsed, or
certified by an external registry unless a separate registry entry proves that.

MCP must not become core runtime. Public verification and SDK adoption remain
higher priority than MCP exposure.
