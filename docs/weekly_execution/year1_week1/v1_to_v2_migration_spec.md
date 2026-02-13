# Year 1 Week 1 — V1 to V2 Migration Specification

## Objective
Replace runtime usage of legacy `backend/app/calendar/calculator.py` with V2-native flows, while preserving API behavior and improving correctness.

## Migration Rules
1. Runtime routes and repository must call V2 directly.
2. Contract fields for date responses must include `date`/`start_date`, `confidence`, `method`, and `engine_version`.
3. Legacy fallback remains temporary until all missing rules are migrated.
4. Legacy tests are retained but separated from runtime acceptance criteria.

## Call-Site Replacement Matrix

| Legacy Source | Current Behavior | V2 Replacement | Behavior Change | Required Test |
|---|---|---|---|---|
| `backend/app/calendar/calculator.py::calculate_festival_date` | bs-month/tithi rules, legacy month model | `calculator_v2.calculate_festival_v2` | Adhik-aware lunar-month semantics | Per-festival date parity test for overlap years |
| `backend/app/calendar/calculator.py::get_upcoming_festivals` | legacy list + legacy rules | `calculator_v2.get_upcoming_festivals_v2` | V2 date ranges and sorting | Upcoming endpoint snapshot test |
| `backend/app/calendar/calculator.py::get_festivals_on_date` | legacy overlap resolver | `calculator_v2.get_festivals_on_date_v2` | Uses V2 overlaps | On-date endpoint contract test |
| `backend/app/calendar/__init__.py` wrappers | wraps v2 but imports legacy types | move shared `DateRange`/`CalendarRule` to neutral `types` module | no API behavior change | Import path stability tests |
| `backend/app/festivals/repository.py::get_dates` | already V2 | no change | none | keep regression coverage |
| `backend/app/festivals/routes.py` | mostly V2 | no change except metadata fields | add `engine_version` to date payloads | response schema tests |
| `backend/app/calendar/routes.py::/festivals/*` | direct V2 usage | no change except metadata fields | add `engine_version` and confidence consistency | contract + integration tests |

## Temporary Compatibility Plan

### Phase A (Week 2 target)
- Keep fallback in `calculator_v2` for legacy-only rule ids.
- Add explicit telemetry/log tag when fallback is hit: `method=fallback_v1`.
- Add warning header in API response when fallback used.

### Phase B (Week 3/4 target)
- Migrate 26 legacy-only rules into V3 format.
- Run parity tests against ground truth and existing `evaluation.csv`.
- Remove fallback import path in `calculator_v2`.

## Blocking Risks (Must Be Addressed)
1. **Signature mismatch risk**  
   In `backend/app/calendar/calculator_v2.py`, fallback currently calls legacy function with `use_overrides` argument.  
   Legacy `calculate_festival_date` signature does not accept this arg.  
   Action: fix fallback adapter signature before relying on fallback.

2. **Coverage risk**  
   V3 has 21 rules; legacy has 47.  
   Immediate fallback removal will reduce festival coverage.

3. **Contract drift risk**  
   Some endpoints return typed models; others return ad-hoc dicts.  
   Action: enforce schema snapshots after each migration step.

## Required Test Plan for Migration

1. `tests/integration/test_v2_route_sources.py`  
- asserts each runtime endpoint source path is V2.

2. `tests/contract/test_date_metadata_contract.py`  
- asserts `confidence`, `method`, `engine_version` presence.

3. `tests/integration/test_fallback_usage.py`  
- verifies fallback is only used for known legacy-only ids.

4. `tests/regression/test_overlap_ground_truth.py`  
- verifies official overlap years remain stable.

5. `tests/regression/test_legacy_parity_subset.py`  
- ensures migrated rule ids match previous expected dates where authoritative.

## Acceptance Criteria (for Week 2 handoff)
1. No active route imports `backend/app/calendar/calculator.py` directly.
2. Any remaining legacy dependency is isolated to one explicit fallback adapter.
3. All migrated endpoints pass metadata contract tests.
4. Accuracy scorecard is reproducible from `backend/tools/evaluate.py`.
