# Benchmark Specification (Year 3 M25)

## Pack Schema
Each benchmark pack is a JSON object:

```json
{
  "pack_id": "string",
  "version": "string",
  "description": "string",
  "calendar_family": "string",
  "cases": [
    {
      "id": "string",
      "endpoint": "/v2/api/...",
      "params": {"k": "v"},
      "assertions": {"dotted.path": "expected"},
      "tolerance": 0,
      "source": "citation"
    }
  ]
}
```

## Assertion Rules
- `assertions` map dotted-path fields to expected values.
- Numeric assertions support tolerance.
- Missing path is a failure.

## Harness Contract
- Input: benchmark pack + base URL (or local in-process API)
- Output report:
  - summary (total/passed/failed/pass_rate/avg_latency_ms)
  - per-case status and error list

## Validator Contract
- Ensures required root/case keys exist.
- Ensures endpoints begin with `/`.
- Ensures assertions object is non-empty.

## File Locations
- Validator: `/Users/rohanbasnet14/Documents/Project Parva/benchmark/validate_pack.py`
- Harness: `/Users/rohanbasnet14/Documents/Project Parva/benchmark/harness.py`
- Packs: `/Users/rohanbasnet14/Documents/Project Parva/benchmark/packs/`
- Results: `/Users/rohanbasnet14/Documents/Project Parva/benchmark/results/`
