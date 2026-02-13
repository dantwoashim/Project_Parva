# Year 1 Week 10 Status (Sidereal/Tropical Configuration)

## Completed
- Added runtime configuration model:
  - `backend/app/engine/ephemeris_config.py`
  - Supports `ayanamsa`: `lahiri|raman|kp`
  - Supports `coordinate_system`: `sidereal|tropical`
  - Supports `ephemeris_mode`: `moshier|swiss` (metadata)
- Threaded optional config into ephemeris calls:
  - `get_sun_longitude(..., config=...)`
  - `get_moon_longitude(..., config=...)`
  - `get_sun_moon_positions(..., config=...)`
- Added engine configuration endpoints:
  - `GET /api/engine/config`
  - `GET /api/engine/health`
- Added ayanamsa tests:
  - `tests/unit/engine/test_ayanamsa.py`

## Extra Fixes
- Fixed ritual timeline schema adapter in frontend:
  - `frontend/src/components/Festival/FestivalDetail.jsx`
- Fixed day-level moon phase naming near new/full moon boundaries:
  - `backend/app/calendar/tithi/__init__.py`
