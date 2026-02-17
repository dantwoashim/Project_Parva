# Year 1 Week 2 — Implementation Status

## Completed This Week

1. **Runtime V2 enforcement improvements**
- `backend/app/calendar/routes.py`
  - unified festival upcoming endpoint to `get_upcoming_festivals_v2(...)`
  - added `engine_version: "v2"` to calendar responses
  - added explicit `confidence`/`method` metadata to festival calculate/upcoming responses
  - added `tithi.confidence` and retained method metadata in conversion/today responses

- `backend/app/festivals/routes.py`
  - ensured upcoming/detail/calendar responses carry `engine_version: "v2"`
  - upcoming festival items now include `method` and `confidence`
  - detail response now includes `date_error` when dates are unavailable

2. **Ritual timeline schema issue fixed**
- Added backend adapter:
  - `backend/app/festivals/adapters.py`
  - normalizes heterogeneous ritual formats into stable `ritual_sequence.days[]`
- Wired adapter into repository load path:
  - `backend/app/festivals/repository.py`
- Extended model with normalized field:
  - `backend/app/festivals/models.py` (`Festival.ritual_sequence`)
- Frontend now prioritizes normalized shape and correctly maps legacy `daily_rituals` list:
  - `frontend/src/components/Festival/FestivalDetail.jsx`

3. **Raised V2 fallback issue fixed**
- Fixed fallback call signature mismatch in:
  - `backend/app/calendar/calculator_v2.py`

4. **Legacy import pressure reduced**
- `backend/app/calendar/__init__.py`
  - removed direct dependency on legacy `calculator.py` for shared types
  - introduced local compatibility `DateRange` type and imported `CalendarRule` from loader

## Test Results

Validated after changes:
- `python3 -m pytest -q tests/integration/test_festival_api.py` → **15 passed**
- `python3 -m pytest -q tests/unit/calendar/test_tithi.py::TestMoonPhaseName tests/unit/calendar/test_calculator.py tests/integration/test_festival_api.py` → **40 passed**
- `python3 -m pytest -q backend/tests/test_ephemeris.py` → **37 passed**
- Evaluation run:
  - `PYTHONPATH=backend python3 backend/tools/evaluate.py --output /tmp/parva_eval_week2.csv`
  - **64/64 passed (100%)**

## Remaining Risk (Explicit)

V2 still has a **temporary fallback** path for festivals not yet migrated to `festival_rules_v3.json`.
- This is functionally stable now.
- To fully remove legacy dependency, migrate remaining legacy-only rules into V3 format and then drop fallback import path.
