# OpenAPI Drift Fix

## Action

Regenerated the public demo OpenAPI mirror:

```bash
PYTHONPATH=backend:. python scripts/release/generate_public_demo_openapi.py
```

## Evidence

- Generation wrote `docs/api-docs/openapi.json` with 387 paths.
- `PYTHONPATH=backend:. python scripts/release/check_public_openapi_drift.py`: pass.
- `python scripts/check_future_bs_public_leakage.py`: pass; public OpenAPI artifacts do not expose private exact Future-BS route prefixes.

No public OpenAPI example was changed to claim official, legal, banking, tax, or
religious authority.

