# Architecture Summary

Project Parva separates public deterministic temporal computation from private or research-only work.

## Public Stable Surface

- Stable v3 routes cover public BS/AD conversion, validation, holidays/observances, fiscal periods, working-day status, Panchanga summaries, trust metadata, and source-aware responses.
- Public verification is runnable through `scripts/release/verify_public.py`.
- Public OpenAPI mirrors are checked for drift.

## Preview And Research Surface

- v4 and v5 surfaces remain preview or research/model-risk where applicable.
- Future-BS capabilities expose metadata and review gates, not public exact unsupported official predictions.
- Private source archives, private kernels, local paths, generated private reports, and research artifacts are not public release material.

## Adapter Layers

- Python SDK: `packages/parva-python`.
- JavaScript/TypeScript SDK: `packages/parva-js`.
- agent tool wrappers: `packages/parva-agent-tools`, public-route only.
- MCP adapter: `packages/parva-mcp-server`, optional and read-only.

## Authority Model

Official bodies decide. Parva encodes, verifies, distributes, and tests machine-readable temporal data and computation boundaries.
