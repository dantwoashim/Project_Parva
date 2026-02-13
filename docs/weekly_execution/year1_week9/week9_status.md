# Year 1 Week 9 Status (UTC & Timezone Audit)

## Completed
- Added engine-level timezone utilities:
  - `backend/app/engine/time_utils.py` (`ensure_utc`, `to_npt`, `from_npt`)
- Added timezone hardening tests:
  - `tests/unit/engine/test_timezone.py`
- Preserved strict UTC checks in Swiss Ephemeris wrapper:
  - `backend/app/calendar/ephemeris/swiss_eph.py`

## Validation
- Edge cases covered: naive datetimes, Nepal midnight crossover, fixed UTC+5:45 behavior, and extreme timezone conversions.
