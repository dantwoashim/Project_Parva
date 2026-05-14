# Deprecation Plan

Generated artifact for Phase 03 canonical runtime consolidation.

## Current Plan

| Path | Phase 03 state | Next action |
| --- | --- | --- |
| `backend/app/calendar/tithi.py` | Converted to shadowed compatibility stub. | Keep until docs and downstream references no longer point at the file. |
| `backend/app/calendar/calculator.py` | Deprecated and allowlisted only for compatibility imports. | Replace old `DateRange` facade usage after migration tests exist. |
| `backend/app/calendar/calculator_v2.py` | Compatibility engine behind the canonical rule service. | Move remaining service internals and observance plugins to rule execution abstractions in a later phase. |
| `backend/app/calendar/festival_rules.json` | Legacy rule source. | Keep until catalog migration proves equivalent coverage. |
| `backend/app/calendar/festival_rules_v3.json` | Legacy rule source. | Keep until catalog migration proves equivalent coverage. |
| `sdk/python` | Compatibility SDK scaffold. | Keep smoke coverage, but do not add new public SDK behavior. |
| `tests/fixtures/plugins` | Test-only source copy. | Keep for unit tests. Runtime reads `data/validation/public/plugins`. |
| `tests/fixtures/tithi_boundaries_30.json`, `tests/fixtures/sankranti_24.json`, `tests/fixtures/adhik_maas_reference.json` | Test-only source copies. | Keep for tests. Runtime reads `data/validation/public/calendar`. |

## Removal Requirements

Before deletion, each candidate must pass:

1. `python scripts/check_canonical_runtime.py`
2. `python -m pytest tests/architecture -q`
3. Focused functional tests for the replacement path
4. Route inventory and documented route checks
5. Public verification

## Rollback Path

All Phase 03 compatibility changes are additive or wrapper-only. If a later
phase removal causes a regression, restore the deprecated path from git history,
re-add the allowlist entry in `config/canonical-runtime.yaml`, and rerun the
canonical checker plus public verification.
