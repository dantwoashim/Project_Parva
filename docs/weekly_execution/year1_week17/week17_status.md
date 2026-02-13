# Year 1 Week 17 Status (Lunar Month Boundary Specification)

## Completed
- Added canonical lunar month spec:
  - `/Users/rohanbasnet14/Documents/Project Parva/docs/LUNAR_MONTH_SPEC.md`
- Added public helper functions for month naming and Adhik detection:
  - `/Users/rohanbasnet14/Documents/Project Parva/backend/app/calendar/lunar_calendar.py`
    - `name_lunar_month(...)`
    - `detect_adhik_maas(...)`
- Added Adhik regression fixture generation tool:
  - `/Users/rohanbasnet14/Documents/Project Parva/backend/tools/generate_adhik_reference.py`
- Generated fixture:
  - `/Users/rohanbasnet14/Documents/Project Parva/tests/fixtures/adhik_maas_reference.json`
- Added regression tests:
  - `/Users/rohanbasnet14/Documents/Project Parva/tests/unit/engine/test_adhik_maas_reference.py`

## Outcome
- Lunar month and Adhik semantics are now documented and test-backed.
