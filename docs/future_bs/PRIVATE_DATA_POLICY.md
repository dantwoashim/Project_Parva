---
status: research
tier: 3
lane: research
last_verified: 2026-05-14
owner: research-team
---

# Future BS Private Data Policy

Future-BS private data includes any material that can reveal exact unpublished
future outputs or private research evidence.

## Private By Default

- exact month-length predictions for unpublished years
- year-range future vectors
- CSV or XLSX exports
- backtest rows, residuals, and model-run internals
- wide-corpus fixtures
- private source files, screenshots, or paid-source extracts
- external sheet comparisons
- schedule, finance, loan, or contract impact simulations using future vectors
- active-learning queues and source-review worklists
- model calibration artifacts and threshold-search artifacts

## Handling Rules

- Keep private data out of public routes, public OpenAPI artifacts, public SDK
  defaults, public examples, and frontend public pages.
- Store generated research artifacts under clearly named research or data paths.
- Do not promote weak or third-party rows into official claim metrics without a
  source-policy review.
- Use aggregate summaries in public docs; keep exact vectors behind private
  profile, research API flag, and authentication.
- If a private artifact is missing, private routes should return a clear error
  naming the generation command instead of fabricating output.

## Access Rule

Private Future-BS routes require a research-private profile, experimental API
enabled, research API enabled, and auth:

```text
PARVA_ROUTE_PROFILE=research_private | internal_lab | full_dev
PARVA_ENABLE_EXPERIMENTAL_API=true
PARVA_ENABLE_RESEARCH_API=true
PARVA_ADMIN_TOKEN=<operator token> or scoped PARVA_API_KEYS
```
