# Year 1 Week 38 Status (Explainability Panel)

## Completed
- Added explain response model and endpoint:
  - `/Users/rohanbasnet14/Documents/Project Parva/backend/app/festivals/models.py`
  - `/Users/rohanbasnet14/Documents/Project Parva/backend/app/festivals/routes.py`
  - Endpoint: `GET /v2/api/festivals/{festival_id}/explain?year=YYYY`
- Added frontend Explain panel UI:
  - `/Users/rohanbasnet14/Documents/Project Parva/frontend/src/components/Festival/ExplainPanel.jsx`
  - `/Users/rohanbasnet14/Documents/Project Parva/frontend/src/components/Festival/ExplainPanel.css`
- Wired detail screen button and API call:
  - `/Users/rohanbasnet14/Documents/Project Parva/frontend/src/components/Festival/FestivalDetail.jsx`
  - `/Users/rohanbasnet14/Documents/Project Parva/frontend/src/services/api.js`
- Added integration tests:
  - `/Users/rohanbasnet14/Documents/Project Parva/tests/integration/test_festival_explain.py`

## Outcome
- Users can now inspect “why this date” with transparent rule-level explanation.
