# Year 1 Week 24 Status (M6 Hardening)

## Completed
- Frontend now carries BS confidence metadata from API:
  - `/Users/rohanbasnet14/Documents/Project Parva/frontend/src/hooks/useCalendar.js`
- UI tooltip now explains official vs estimated BS dates:
  - `/Users/rohanbasnet14/Documents/Project Parva/frontend/src/components/Calendar/LunarPhase.jsx`
- Added explicit estimated conversion wrappers for tooling and overlap diagnostics:
  - `/Users/rohanbasnet14/Documents/Project Parva/backend/app/calendar/bikram_sambat.py`
  - `bs_to_gregorian_estimated(...)`
  - `estimated_bs_to_gregorian(...)`
  - `estimated_gregorian_to_bs(...)`
- Added compatibility test for wrapper aliases:
  - `/Users/rohanbasnet14/Documents/Project Parva/tests/unit/calendar/test_bikram_sambat.py`

## Outcome
- M6 end-to-end confidence UX is now present in backend and frontend.
