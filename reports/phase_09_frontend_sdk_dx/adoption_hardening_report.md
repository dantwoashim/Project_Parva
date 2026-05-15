# Adoption Hardening Report

## What is easier now

- `docs/QUICKSTART.md` gives a copy-paste path for toolchain checks, REST calls,
  Python SDK calls, JS SDK calls, trust/source metadata, and review boundaries.
- `docs/SDK_STRATEGY.md` names `packages/parva-python` and `packages/parva-js`
  as canonical SDKs and keeps `sdk/python` as compatibility scaffolding.
- `docs/API_VERSIONING_AND_DEPRECATION.md` states v3/v4/v5/v2 semantics.
- `scripts/frontend/check_component_size.py` gives a measurable path for
  decomposing large frontend files without rewriting the UI in this sprint.
- Commercial and enterprise docs now center the BS Date Risk Audit wedge.

## Current frontend size risk

The largest known frontend risk remains `frontend/src/redesign/ParvaExperience.jsx`.
The checker starts in warning mode so it can be added to review workflows without
blocking unrelated fixes immediately.

## Claim boundary

No new official, government, legal, tax, banking, payroll, religious, Future-BS
official-date, or certification authority claim was added.
