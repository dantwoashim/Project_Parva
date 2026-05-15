---
status: research
tier: 3
lane: research
last_verified: 2026-05-14
owner: research-team
---

# Future BS Research Boundary

Status: public/private governance boundary.

The Future-BS subsystem is a research and model-risk layer. It may be used to
study unpublished BS month-length behavior, source disagreement, risk labels,
and schedule impact. It is not an official calendar publication service.

All unpublished outputs must carry:

```text
publication_status = computed_prediction_not_official
```

## Public Surface

Public profiles may expose only metadata:

- capability summaries
- source-policy summaries
- methodology summaries
- claim-boundary text
- risk-label vocabulary
- aggregate validation posture

Public profiles must not expose exact future month lengths, generated future
vectors, model-run internals, residual rows, wide-corpus fixtures, private
source files, backtest tables, external sheet comparisons, schedule-impact
simulation, or calendar model-risk prediction payloads.

## Private Research Surface

Exact Future-BS and calendar model-risk routes require all of these controls:

```text
PARVA_ROUTE_PROFILE=research_private | internal_lab | full_dev
PARVA_ENABLE_EXPERIMENTAL_API=true
PARVA_ENABLE_RESEARCH_API=true
PARVA_ADMIN_TOKEN=<operator token> or scoped PARVA_API_KEYS
```

Private schema publication additionally requires:

```text
PARVA_SHOW_PRIVATE_SCHEMA=true
```

The `full` development profile is not a research-private route profile. Use
`full_dev`, `research_private`, or `internal_lab` for exact Future-BS research
routes.

## Boundary Failure

If public output contains an exact future vector, private artifact path, official
future-calendar claim, or unqualified high-confidence future claim, treat it as a
release blocker and run:

```bash
python scripts/check_future_bs_public_leakage.py
```
