---
status: public-beta
tier: 1
lane: core
last_verified: 2026-05-14
owner: platform-team
---

# Performance Budgets

Project Parva uses route-level latency and payload budgets to keep public,
preview, and enterprise surfaces operationally bounded.

The machine-readable registry lives at:

```text
config/performance-budgets.yaml
```

## Budget Lanes

| Lane | Enforcement |
| --- | --- |
| `stable_core` | Local p95 breaches fail the latency smoke script. |
| `stable_public` | Local warm p95 breaches fail the latency smoke script. |
| `public_preview` | Breaches warn unless promoted to stable. |
| `developer_preview` | Breaches warn and must be reviewed before public promotion. |
| `enterprise_preview` | Breaches warn and require deployment-specific load testing. |
| `protocol_draft` | Breaches warn while protocol status remains draft. |

## Local Smoke Command

```bash
python scripts/perf/route_latency_smoke.py --profile public_reference --output tmp/public_reference_latency_baseline.json
```

On Windows systems where `python` is not Python 3.11, use the explicit Python
3.11 executable documented in `docs/DEVELOPMENT.md`.

## Initial Public Reference Budgets

| Route family | Local p95 target | Notes |
| --- | ---: | --- |
| Health and readiness | 25 to 50 ms | Must stay cheap and independent of heavy compute. |
| BS/AD conversion | 75 ms | Uses indexed lookup for supported official range. |
| Calendar today | 300 ms warm | Uses bounded compute and metadata generation. |
| Festivals upcoming | 300 ms warm | Requires cache or precompute warm path. |
| Protocol version | 100 ms | Protocol metadata should be static or near-static. |

Preview routes for panchanga, kundali, muhurta, TimeGraph, RuleLang, Impact,
Agent, and billing are in the YAML registry so future promotion has explicit
budget evidence.

## Payload Rules

Routes with unbounded lists must expose `limit`, bounded `days`, or bounded
profile filters. The budget registry includes maximum payload sizes so a fast
route cannot still become an operational risk through oversized responses.

## Current Baseline

The local baseline report is:

```text
tmp/public_reference_latency_baseline.json
```

The report is created by in-process FastAPI requests for reproducibility. A
deployed smoke should be run separately before release promotion.
