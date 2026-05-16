# Duplicate Runtime Cleanup

The duplicate runtime paths were reviewed for public-beta distribution.

## Findings

- `backend/app/calendar/tithi/` is the canonical tithi package. The shadow
  `backend/app/calendar/tithi.py` file is not the imported runtime module.
- `backend/app/calendar/calculator.py` and
  `backend/app/calendar/calculator_v2.py` are retained as compatibility
  modules for legacy tools and tests. Public route imports are blocked from
  using them as primary runtime paths by `scripts/check_canonical_runtime.py`.
- `backend/app/calendar/festival_rules.json` and
  `backend/app/calendar/festival_rules_v3.json` remain legacy rule sources.
  Canonical festival runtime paths are `backend/app/rules/service.py`,
  `backend/app/rules/catalog_v4.py`, and `data/festivals`.

## Current Decision

No risky deletion was made in this sprint. The duplicate paths are documented
as compatibility-only and have removal targets in `docs/DEPRECATION_POLICY.md`.

## Verification

Run:

```bash
python scripts/check_canonical_runtime.py
python -m pytest tests/runtime/test_canonical_runtime_imports.py -q
```

The public route import checks must stay green before any later removal.
