---
status: research
tier: 3
lane: research
last_verified: 2026-05-14
owner: research-team
---

# Future BS Public API Boundary

The public Future BS surface is intentionally narrow.

## Public Endpoint

```http
GET /v4/api/future-bs/capabilities
```

This endpoint describes the research layer, source-policy posture, claim boundaries, and supported capability categories.

## Private Endpoints

Direct future month-length values, range prediction, CSV/XLSX export, backtests, residuals, explanation payloads, boundary-risk payloads, model-run metadata, import tools, external-sheet comparison, and schedule-impact simulation are private deployment surfaces.

They are not part of the public API profile and should not appear in public OpenAPI output.

Private endpoints require:

```text
PARVA_ROUTE_PROFILE=research_private | internal_lab | full_dev
PARVA_ENABLE_EXPERIMENTAL_API=true
PARVA_ENABLE_RESEARCH_API=true
PARVA_ADMIN_TOKEN=<operator token> or scoped PARVA_API_KEYS
```

## Claim Boundary

Future outputs from the research layer remain:

```text
computed_prediction_not_official
```

They are for validation, audit, comparison, and risk detection. Official publication, legal interpretation, tax treatment, banking-contract finalization, and production financial decisions require the relevant authority or institution's own approval.
