# Explainability Assistant Notes

## What is implemented
- Human-readable explanation endpoint:
  - `GET /v2/api/festivals/{id}/explain?year=YYYY`
- Deterministic technical trace endpoint:
  - `GET /v2/api/explain/{trace_id}`
- Trace listing endpoint:
  - `GET /v2/api/explain?limit=20`

## Frontend integration
- `ExplainPanel` shows:
  - human-readable summary and steps
  - technical trace (step types + math expressions + rule/source hints)

## Validation goals
- Same festival/year should return same `calculation_trace_id`.
- Trace endpoint must return structured steps for audit/review sessions.
