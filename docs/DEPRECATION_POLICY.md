# Deprecation Policy

Project Parva keeps public behavior stable while moving duplicate truth paths to
one canonical runtime per concept.

## Labels

| Label | Meaning |
| --- | --- |
| `canonical_public` | The path is the public source of truth. |
| `canonical_public_alpha` | The path is canonical, but the package surface is still alpha. |
| `compatibility_scaffold` | The path may remain for old imports or installs, but new behavior must land in the canonical path. |
| `legacy_rule_source` | The path is retained for migration or fallback only. |
| `shadowed_compatibility_stub` | The path is not the imported runtime path and must not contain competing logic. |
| `test_only_source_copy` | The path is allowed for tests, while runtime reads the public validation copy. |

## Requirements

- Every deprecated path must have a replacement in `config/canonical-runtime.yaml`.
- Public routes must not import deprecated modules unless the registry allows a
  specific compatibility wrapper.
- Runtime code must not read test fixtures for public quality claims.
- Deprecated SDK paths may keep smoke coverage, but new SDK tests and docs must
  target canonical packages.
- Removing a deprecated path requires passing the canonical checker,
  architecture tests, route inventory, documented route checks, backend smoke,
  and public verification.

## Current Deprecations

| Area | Deprecated or compatibility path | Replacement |
| --- | --- | --- |
| Tithi | `backend/app/calendar/tithi.py` | `backend/app/calendar/tithi/` |
| Festivals | `backend/app/calendar/calculator.py` | `backend/app/rules/service.py` |
| Festivals | `backend/app/calendar/calculator_v2.py` | `backend/app/rules/service.py` |
| Festival rules | `backend/app/calendar/festival_rules.json`, `backend/app/calendar/festival_rules_v3.json` | `data/rules`, `backend/app/rules/catalog_v4.py` |
| Python SDK | `sdk/python` | `packages/parva-python` |
| Runtime validation | `tests/fixtures/` | `data/validation/public/` |

## Removal Gate

A deprecated path can be deleted only when:

1. The replacement is listed in the canonical registry.
2. Public route imports no longer reference the deprecated path.
3. Compatibility smoke tests either pass or are intentionally retired in the
   same change.
4. Reports document the deletion evidence and rollback path.
5. Public verification remains green.
