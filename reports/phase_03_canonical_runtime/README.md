# Phase 03 Canonical Runtime Consolidation Report

Generated artifact for Phase 03 verification evidence.

## Status

In progress. The canonical registry, checker, architecture tests, runtime
validation data copies, and public runtime import cleanup have been implemented.
Final public verification is still pending in this report until the full command
set completes.

## Scope Audited

- `parva_codex_phase_files/AGENTS.md`
- `parva_codex_phase_files/phase_03_canonical_runtime_consolidation.md`
- Root `AGENTS.md`
- Phase 01 generated artifacts: `reports/phase_01_baseline/canonical_runtime_discovery.md`, `reports/phase_01_baseline/duplicate_truth_paths.md`, `reports/phase_01_baseline/dead_code_candidates.md`
- Canonical runtime modules under `backend/app/calendar/`, `backend/app/rules/`, `backend/app/festivals/`, `backend/app/core/`, `backend/app/reliability/`, and `backend/app/api/`
- SDK paths `packages/parva-python`, `packages/parva-js`, and `sdk/python`
- Runtime validation sources under `tests/fixtures/`, `data/validation/public/`, and `backend/data/public_artifacts/`

## Changes Made

- Added `config/canonical-runtime.yaml` as the machine-readable canonical runtime registry.
- Added `scripts/check_canonical_runtime.py` and wired it into `scripts/release/verify_public.py`.
- Added architecture tests for registry completeness, research/private import boundaries, runtime fixture boundaries, and deprecated import boundaries.
- Moved public runtime validation inputs to `data/validation/public/calendar` and `data/validation/public/plugins`.
- Updated public runtime code to read validation inputs from `data/validation/public`, not `tests/fixtures`.
- Changed public festival calculation route and calendar surface fallback to use `app.rules.service`.
- Updated the engine manifest so festival canonical runtime is the rule service, catalog, and repository, with calculator engines labeled as compatibility.
- Replaced the shadowed `backend/app/calendar/tithi.py` implementation with a compatibility stub.
- Added canonical runtime and deprecation docs.
- Updated SDK docs so `packages/parva-python` and `packages/parva-js` are canonical and `sdk/python` is compatibility scaffolding.

## Verification Matrix

| Command | Result | Evidence |
| --- | --- | --- |
| `python scripts/check_canonical_runtime.py` | Pass | `Canonical runtime registry check passed.` |
| `python -m pytest tests/architecture -q` | Pass | `10 passed in 1.99s` |
| `python scripts/release/check_route_inventory.py` | Pending | Not run yet in this report. |
| `python scripts/release/check_documented_routes.py` | Pending | Not run yet in this report. |
| `python scripts/release/check_backend_smoke.py` | Pending | Not run yet in this report. |
| `python -m ruff check backend tests scripts sdk packages/parva-python` | Pending | Not run yet in this report. |
| `pytest -q -m "not private_source and not wide_corpus and not research_artifact" --maxfail=20` | Pending | Not run yet in this report. |
| `python scripts/release/verify_public.py` | Pending | Not run yet in this report. |

## Acceptance Checklist

1. Config registry exists and covers major domain concepts: implemented, checker passing.
2. Canonical runtime docs exist: implemented.
3. Checker exists and passes: implemented and passing.
4. Architecture tests enforce canonical boundaries: implemented and passing.
5. Canonical paths documented for conversion, tithi, festivals, source/confidence, SDKs, and validation artifacts: implemented.
6. Deprecated and compatibility paths labeled and tested: implemented.
7. Public runtime code does not depend on `tests/fixtures` for public quality claims: implemented, architecture check passing.
8. Dead-code candidates classified and safe archives/deletions recorded: implemented in generated artifact `reports/phase_03_canonical_runtime/deletions_and_archives.md`.
9. Public verification remains green: pending full gate.

## Remaining Blockers

None known yet. Full verification is pending.

## Later-Phase Backlog

- Remove compatibility calculator imports from `app.rules.execution` and observance plugins after route migration tests cover the replacement path.
- Retire `sdk/python` after canonical package adoption and compatibility import telemetry are no longer needed.
- Regenerate historical snapshot artifacts if a later phase wants the old manifest payloads to match the Phase 03 registry labels.
