# Duplicate Resolution Log

Generated artifact for Phase 03 canonical runtime consolidation.

## Resolved In Phase 03

| Duplicate area | Prior state | Phase 03 resolution | Verification |
| --- | --- | --- | --- |
| Tithi package versus file | `backend/app/calendar/tithi.py` and `backend/app/calendar/tithi/` both contained tithi logic. Python imported the package path. | `backend/app/calendar/tithi.py` is now a compatibility stub that re-exports the package. The package directory is canonical. | `python scripts/check_canonical_runtime.py` passed. |
| Festival route engine | `backend/app/calendar/routes.py` imported `app.calendar.calculator_v2` directly. | The route now uses `app.rules.service.get_rule_service()`. | Architecture forbidden import check passed. |
| Calendar surface festival fallback | `backend/app/services/calendar_surface_service.py` imported `app.calendar.calculator_v2` directly. | The fallback now uses `app.rules.service.get_rule_service()`. | Architecture forbidden import check passed. |
| Plugin quality validation | Public engine quality read from `tests/fixtures/plugins`. | Runtime copies now live under `data/validation/public/plugins`. | Runtime fixture dependency check passed. |
| Boundary suite validation | Reliability boundary suite read from `tests/fixtures`. | Runtime copies now live under `data/validation/public/calendar`. | Runtime fixture dependency check passed. |
| SDK truth paths | `sdk/python` and `packages/parva-python` both looked like install targets. | `packages/parva-python` and `packages/parva-js` are canonical. `sdk/python` is compatibility scaffolding. | Registry and SDK path checks passed. |

## Compatibility Kept Intentionally

| Path | Reason kept | Replacement |
| --- | --- | --- |
| `backend/app/calendar/calculator.py` | Legacy `DateRange` and old calculator compatibility exports. | `app.rules.service` |
| `backend/app/calendar/calculator_v2.py` | Compatibility engine behind `FestivalRuleService` and selected observance plugins. | `app.rules.service` |
| `backend/app/calendar/festival_rules.json` | Legacy rule source during catalog migration. | `data/rules` and `app.rules.catalog_v4` |
| `backend/app/calendar/festival_rules_v3.json` | Legacy rule source during catalog migration. | `data/rules` and `app.rules.catalog_v4` |
| `sdk/python` | Legacy Python SDK import and smoke path. | `packages/parva-python` |

## Not Fixed In Phase 03

- `backend/tools/*` still contains evaluator scripts that import `app.calendar.calculator_v2`. These are developer tools, not public route runtime.
- Historical snapshot JSON still records older manifest payloads. Regenerating snapshots is a later artifact-management task.
