---
status: research
tier: 3
lane: research
last_verified: 2026-05-14
owner: research-team
---

# Future BS Accuracy Reproducibility

Future-BS accuracy claims must be reproducible from versioned code, source
policy, corpus snapshot, and model-run metadata.

## Required Evidence

Any accuracy report must include:

- source policy name
- evidence window
- corpus size and coverage
- train and evaluation boundaries
- model version and calibration version
- run id and artifact hash when available
- overall accuracy
- high-confidence accuracy
- wrong high-confidence count
- false-confidence rate
- wrong-GREEN count
- residual summary
- excluded source tiers and invalid rows
- blockers and data limitations

## Public Claim Boundary

Official/public claims must use strict official or reviewed source policy. Broad
all-reference stress tests may be used for residual analysis and risk discovery,
but not for official-grade public claims.

All unpublished predictions remain:

```text
publication_status = computed_prediction_not_official
```

## Reproducibility Commands

The public research-governance lane is:

```bash
python scripts/check_future_bs_public_leakage.py
pytest -q -m "not private_source and not wide_corpus and not research_artifact" tests/future_bs tests/accuracy tests/artifacts tests/performance --maxfail=20
python -m pytest tests/future_bs -q
python scripts/release/check_openapi_drift.py
python scripts/release/check_route_inventory.py
python scripts/release/verify_public.py
```

Run private or wide-corpus checks only in a private research environment with the
required source artifacts present.
