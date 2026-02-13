# Year 1 Week 15 Status (API Integration & Method Metadata)

## Completed
- Upgraded tithi metadata in API responses:
  - `/api/calendar/convert`
  - `/api/calendar/today`
  - `/api/calendar/panchanga`
- Added new endpoint:
  - `GET /api/calendar/tithi?date=YYYY-MM-DD[&latitude=&longitude=]`
- Added contract tests for tithi metadata:
  - `tests/contract/test_tithi_response.py`
- Frontend integration updated:
  - `frontend/src/services/api.js` (today/panchanga/tithi calls)
  - `frontend/src/hooks/useCalendar.js` (backend-first, local fallback)
  - `frontend/src/components/Calendar/LunarPhase.jsx` (method/confidence tooltip)

## Extra Fixes Included
- `today` and `convert` now use `method: ephemeris_udaya` when sunrise path succeeds.
- Response fields now include:
  - `confidence`
  - `reference_time`
  - `sunrise_used`

## Outcome
- Tithi responses are now self-describing and evaluator-friendly.
- Frontend now surfaces whether values are exact or estimated.
