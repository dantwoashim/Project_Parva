# Year 1 Week 16 Status (M4 Hardening)

## Completed
- Removed local synodic approximation from active frontend calendar path:
  - `/Users/rohanbasnet14/Documents/Project Parva/frontend/src/hooks/useCalendar.js`
- Added graceful unknown-paksha handling for fallback UI:
  - `/Users/rohanbasnet14/Documents/Project Parva/frontend/src/components/Calendar/LunarPhase.jsx`
- Refactored tithi duration estimator to sample ephemeris windows (no fixed synodic constant):
  - `/Users/rohanbasnet14/Documents/Project Parva/backend/app/calendar/tithi/tithi_boundaries.py`
- Added runtime profiler and generated performance output:
  - `/Users/rohanbasnet14/Documents/Project Parva/backend/tools/profile_tithi.py`
  - `/Users/rohanbasnet14/Documents/Project Parva/docs/weekly_execution/year1_week16/tithi_performance.md`
- Updated evaluator technical report to reflect active ephemeris+udaya path.

## Outcome
- Active `/today` and panchanga flows are now consistently ephemeris-first.
- Tithi runtime remains comfortably under the `<50ms` target.
