# Year 2 Week 10 Status (Variant Engine Implementation)

## Completed
- Added variant calculation service:
  - `/Users/rohanbasnet14/Documents/Project Parva/backend/app/rules/variants.py`
- Added festival variant endpoint:
  - `GET /v2/api/festivals/{festival_id}/variants?year=YYYY`
  - implemented in `/Users/rohanbasnet14/Documents/Project Parva/backend/app/festivals/routes.py`
- Added integration test coverage for variants endpoint.

## Outcome
- First-pass regional observance variants are now API-addressable.
