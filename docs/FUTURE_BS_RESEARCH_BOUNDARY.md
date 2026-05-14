---
status: public-beta
tier: 1
lane: core
last_verified: 2026-05-14
owner: platform-team
---

# Future BS Research Boundary

Status: Phase 07 research-private boundary.

Future-BS work is a research and model-risk subsystem. Public Parva surfaces may
describe its methodology, source policy, uncertainty, risk labels, and claim
boundary. Public Parva surfaces must not expose exact future month lengths,
future date mappings outside verified public data, private calibration
artifacts, model-run internals, residual tables, or generated future vectors.

All future-BS outputs remain labeled:

```text
publication_status = computed_prediction_not_official
```

## Publicly Allowed

- capability summaries
- methodology and source-tier summaries
- risk-label vocabulary
- aggregate validation posture
- warnings and claim-boundary text
- route and SDK policy documentation

## Private By Default

- direct prediction endpoints
- range prediction endpoints
- exports
- backtests
- residual analysis
- exact explain and boundary outputs
- model-run inventories
- sheet comparison workflows
- schedule, loan, or contract impact simulation using future vectors
- private source files and unpublished artifacts

## Deployment Rule

Public deployments should keep:

```text
PARVA_ENABLE_EXPERIMENTAL_API=false
PARVA_SHOW_PRIVATE_SCHEMA=false
PARVA_ALLOW_PUBLIC_UNVERIFIED_FUTURE_CONVERSION=false
```

Research routes require an explicit private profile such as `research_private`,
`internal_lab`, or `full_dev`, plus the experimental API flag, the research API
flag, and authentication:

```text
PARVA_ENABLE_EXPERIMENTAL_API=true
PARVA_ENABLE_RESEARCH_API=true
PARVA_ADMIN_TOKEN=<operator token> or scoped PARVA_API_KEYS
```

Private OpenAPI schema exposure still requires:

```text
PARVA_SHOW_PRIVATE_SCHEMA=true
```

The detailed Phase 07 policy set lives under `docs/future_bs/`:

- `RESEARCH_BOUNDARY.md`
- `PUBLIC_CLAIMS_POLICY.md`
- `PRIVATE_DATA_POLICY.md`
- `ACCURACY_REPRODUCIBILITY.md`
- `WRONG_GREEN_POLICY.md`
- `MODEL_REGISTRY.md`

## Claim Rule

Future-BS public language may say Parva computes and studies calendar-risk
signals. It may not say Parva publishes official future BS dates or guarantees
future month lengths.
