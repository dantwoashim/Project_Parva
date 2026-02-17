# Year 1 Week 4 — Hardening & Release Status

## Completed

1. Added migration contract integration tests
- `backend/tests/test_v2_migration.py`
- Verifies:
  - V2 metadata (`engine_version`, `method`, `confidence`) on migrated endpoints
  - normalized ritual timeline presence for festival detail
  - runtime route files do not directly import legacy calculator module

2. Added ground-truth regression tests
- `backend/tests/test_ground_truth_regression.py`
- Uses Week 3 baseline `data/ground_truth/baseline_2080_2082.json`
- Guards:
  - all usable baseline entries resolve with V2 + overrides
  - no drift greater than 1 day
  - exact-rate floor remains >=80%

3. Marked legacy engine as deprecated
- `backend/app/calendar/calculator.py`
- Import now emits `DeprecationWarning` with migration message.

4. Updated docs for runtime V2 policy and metadata
- `README.md`
- `TECHNICAL_README.md`

5. Updated changelog
- `CHANGELOG.md` includes Week 4 summary and verification notes.

## Test Runs (Week 4)

```bash
python3 -m pytest -q backend/tests/test_v2_migration.py
python3 -m pytest -q backend/tests/test_ground_truth_regression.py
python3 -m pytest -q backend/tests/test_api_calendar.py
python3 -m pytest -q tests/integration/test_festival_api.py
```

All passed in this session.

## Risk / Remaining Work

1. `calculator_v2` still has fallback to legacy `calculator.py` for non-migrated rule IDs.
2. This keeps coverage, but means legacy path is still reachable for some festivals.
3. Next release objective should be:
- migrate remaining legacy-only rules to V3-native format,
- remove fallback path,
- make deprecation warning informational only (or delete module after parity).

## Release Notes (M1 Month End Readiness)

- Runtime route layer is now V2-aligned with explicit metadata.
- Ground-truth regression gate is now enforced in tests.
- Legacy usage is visible and auditable via deprecation warning.
