# Import Boundary Report

Generated artifact for Phase 03 canonical runtime consolidation.

## Enforced Boundaries

| Boundary | Enforcement |
| --- | --- |
| Canonical paths exist | `scripts/check_canonical_runtime.py` validates registry paths and `app.*` modules. |
| Referenced tests exist | `scripts/check_canonical_runtime.py` validates tests or planned TODO reasons. |
| Deprecated modules are not imported from new public paths | `scripts/check_canonical_runtime.py` validates deprecated import allowlists. |
| Public route modules do not import research/private modules | `tests/architecture/test_no_public_route_imports_research_private.py` calls the checker. |
| Public runtime does not read `tests/fixtures` | `tests/architecture/test_no_runtime_tests_fixture_dependency.py` calls the checker. |
| Forbidden route imports stay absent | `tests/architecture/test_deprecated_modules_not_imported_by_public_routes.py` calls the checker. |

## Public Route Modules Checked

- `app.calendar.routes`
- `app.festivals.routes`
- `app.api.calendar_routes`
- `app.api.festival_routes`
- `app.api.engine_routes`
- `app.api.reliability_routes`
- `app.api.public_artifacts_routes`

## Deprecated Module Allowlist

| Deprecated module | Allowed importer |
| --- | --- |
| `app.calendar.calculator` | `app.calendar`, `app.calendar.calculator_v2` |
| `app.calendar.calculator_v2` | `app.calendar`, `app.rules.service`, `app.rules.execution`, `app.rules.plugins.*` |

## Current Result

`python scripts/check_canonical_runtime.py` passed with no boundary failures.
