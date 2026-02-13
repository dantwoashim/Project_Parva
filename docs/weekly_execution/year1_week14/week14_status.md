# Year 1 Week 14 Status (Udaya Tithi Implementation)

## Completed
- Added convenience API for sunrise tithi:
  - `calculate_tithi_at_sunrise()` in `backend/app/calendar/tithi/tithi_core.py`
- Added vriddhi detection:
  - `detect_vriddhi()` in `backend/app/calendar/tithi/tithi_udaya.py`
- Added ksheepana detection:
  - `detect_ksheepana()` in `backend/app/calendar/tithi/tithi_udaya.py`
- Added boundary-corpus generator:
  - `backend/tools/generate_tithi_boundary_fixture.py`
- Generated 30-case boundary corpus:
  - `tests/fixtures/tithi_boundaries_30.json`
- Added boundary tests:
  - `tests/unit/engine/test_tithi_boundaries_30.py`

## Outcome
- Vriddhi/ksheepana logic is now deterministic and sunrise-based.
- Boundary-sensitive dates are covered by dedicated regression tests.
