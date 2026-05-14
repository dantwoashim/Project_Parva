# Compatibility Wrappers

Generated artifact for Phase 03 canonical runtime consolidation.

## Active Wrappers

| Wrapper | Status | Canonical replacement |
| --- | --- | --- |
| `backend/app/calendar/tithi.py` | Shadowed compatibility stub. It re-exports from `app.calendar.tithi`. | `backend/app/calendar/tithi/` |
| `backend/app/calendar/__init__.py` | Compatibility facade for older calendar imports. | Direct imports from canonical modules and services. |
| `backend/app/api/calendar_routes.py` | Compatibility API module that includes `app.calendar.routes`. | `app.calendar.routes` |
| `backend/app/api/festival_routes.py` | Compatibility API module that includes `app.festivals.routes`. | `app.festivals.routes` |
| `sdk/python` | Legacy Python SDK scaffold and smoke path. | `packages/parva-python` |

## Compatibility Engines

| Engine | Status | Allowed callers |
| --- | --- | --- |
| `app.calendar.calculator.py` | Deprecated legacy calculator. | `app.calendar`, `app.calendar.calculator_v2` |
| `app.calendar.calculator_v2.py` | Compatibility engine behind the canonical festival rule service. | `app.rules.service`, `app.rules.execution`, `app.rules.plugins.*`, `app.calendar` |

## Rule

New production imports should use canonical modules from
`config/canonical-runtime.yaml`. Adding a new compatibility caller requires a
registry update and a passing canonical runtime check.
