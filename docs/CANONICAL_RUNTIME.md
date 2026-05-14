# Canonical Runtime

Phase 03 defines the canonical runtime paths for public Project Parva behavior.
The machine-readable registry is `config/canonical-runtime.yaml`. The file uses
JSON syntax so it is also valid YAML and can be parsed without extra runtime
dependencies.

## Scope

The registry covers these public concepts:

| Concept | Canonical path | Compatibility or deprecated path |
| --- | --- | --- |
| BS and AD conversion | `backend/app/services/calendar_conversion_service.py`, `backend/app/calendar/bikram_sambat.py` | `backend/app/calendar/__init__.py` re-exports remain compatibility only |
| Tithi and panchanga | `backend/app/calendar/tithi/`, `backend/app/calendar/panchanga.py` | `backend/app/calendar/tithi.py` is a shadowed compatibility stub |
| Festivals and observances | `backend/app/rules/service.py`, `backend/app/rules/catalog_v4.py`, `backend/app/festivals/` | `backend/app/calendar/calculator.py`, `backend/app/calendar/calculator_v2.py`, and legacy rule JSON stay behind compatibility wrappers |
| Source and confidence taxonomy | `backend/app/core/source_metadata.py`, trust infrastructure, source validation | local ad hoc source strings are not canonical |
| Holiday release handling | `backend/app/services/trust_infrastructure_service.py`, `data/public/releases/`, `data/public/trust/` | calendar overrides remain compatibility evidence inputs |
| Fiscal and working-day logic | `backend/app/calendar/fiscal.py`, `backend/app/services/enterprise_calendar_service.py`, `backend/app/services/compliance_service.py` | none |
| RuleLang executor | `backend/app/services/rulelang_service.py`, `backend/app/api/rules_routes.py`, `data/rules/public/` | none |
| Trust release artifact model | `backend/app/services/trust_infrastructure_service.py`, `backend/app/services/trust_surface_service.py`, `data/public/` | none |
| Protocol schema source | `backend/app/services/protocol_service.py`, `specs/parva-protocol/`, `schemas/parva-protocol/` | none |
| CLI and verification scripts | `scripts/parva_validate.py`, `scripts/release/verify_public.py`, `scripts/check_canonical_runtime.py` | none |
| Frontend API client | `frontend/src/services/apiCore.js`, `frontend/src/services/api.js`, `frontend/src/services/apiContracts.js` | page-specific clients are compatibility helpers |
| SDKs | `packages/parva-python`, `packages/parva-js` | `sdk/python` is compatibility scaffolding |
| Runtime validation artifacts | `data/validation/public/`, `backend/data/public_artifacts/` | `tests/fixtures/` is test-only and not a public runtime dependency |

## Rules

1. Public route modules call canonical services, not deprecated engines.
2. Public route modules must not import research or private future-BS modules.
3. Public runtime code must not read from `tests/fixtures/`.
4. Tests referenced by the registry must exist, unless they are marked
   `planned_todo` with a reason.
5. Compatibility modules may remain only when the registry labels them and the
   checker allows the import explicitly.
6. SDK tests target `packages/parva-python` and `packages/parva-js`. The
   `sdk/python` path is smoke-tested as compatibility only.

## Verification

Run:

```bash
python scripts/check_canonical_runtime.py
python -m pytest tests/architecture -q
```

The public reproducibility gate also runs the canonical runtime checker through
`scripts/release/verify_public.py`.

## Runtime Artifact Policy

Public route quality, plugin quality, and reliability outputs use
`data/validation/public/` or `backend/data/public_artifacts/`. Tests can still
keep their own fixtures under `tests/fixtures/`, but production code must not
load them directly.

## Future Phases

Phase 03 documents later-phase cleanup candidates in the generated artifact
`reports/phase_03_canonical_runtime/` generated artifact directory. Later
phases can remove compatibility paths only after the registry, architecture
tests, and route smoke tests stay green.
