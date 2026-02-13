# Year 1 Week 6 Status (Module Extraction)

## Completed
- Added API-layer wrappers:
  - `backend/app/api/calendar_routes.py`
  - `backend/app/api/festival_routes.py`
  - `backend/app/api/location_routes.py`
  - `backend/app/api/provenance_routes.py`
  - `backend/app/api/engine_routes.py`
- Switched application composition to API layer:
  - `backend/app/main.py` now imports routers from `app.api` only.
- Added rule-service wrapper and wired festival flow:
  - `backend/app/rules/service.py`
  - `backend/app/festivals/routes.py` now uses `get_rule_service()`
  - `backend/app/festivals/repository.py` now uses `get_rule_service()`

## Notes
- Extraction is implemented as a safe cutover (façade pattern), not a destructive file move.
- This preserves compatibility while enforcing cleaner module boundaries in runtime wiring.
