# Explainability Trace Spec (Year 3 Week 31-34)

## Trace Endpoint
- `GET /v2/api/explain/{trace_id}`
- `GET /v2/api/explain?limit=20`

## Trace Structure
```json
{
  "trace_id": "tr_...",
  "trace_type": "festival_date_explain",
  "subject": {"festival_id": "dashain"},
  "inputs": {"year": 2026},
  "outputs": {"start_date": "2026-10-10"},
  "steps": [
    {
      "step_type": "load_rule",
      "input": {},
      "output": {},
      "rule_id": "dashain",
      "source": "festival_rules_v3.json",
      "math_expression": "..."
    }
  ],
  "provenance": {"snapshot_id": "snap_..."}
}
```

## Determinism Rule
- `trace_id` is generated from canonical payload hash (excluding timestamp).
- Same rule + input + output path results in same `trace_id`.

## Usage
- Festival explain endpoint returns `calculation_trace_id`.
- UI can fetch the full technical trace for evaluator-grade explanation.
