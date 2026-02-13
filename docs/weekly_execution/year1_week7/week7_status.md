# Year 1 Week 7 Status (Type Contracts & Validation)

## Completed
- Added strict engine contracts with validation:
  - `backend/app/engine/types.py`
- Added conversion validation rule:
  - `source_range` required when confidence is `estimated`.
- Added contract tests:
  - `tests/contract/test_response_shapes.py`
- Added API metadata headers globally:
  - `X-Parva-Engine`
  - `X-Parva-Ephemeris`

## Improvements
- Updated deprecated Pydantic `class Config` usage in:
  - `backend/app/festivals/models.py`
  - `backend/app/calendar/calculator.py`
  - `backend/app/calendar/festival_rules_loader.py`
- Updated deprecated FastAPI `Query(example=...)` usage to `examples=...`.
