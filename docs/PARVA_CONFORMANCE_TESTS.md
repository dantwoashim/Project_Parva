# Parva Conformance Tests

## Runner
```bash
PYTHONPATH=backend python3 scripts/spec/run_conformance_tests.py
```

## Minimum Checks
1. `/v3/api/calendar/convert` returns core fields + policy/provenance
2. `/v3/api/calendar/panchanga` returns panchanga + ephemeris metadata
3. `/v3/api/festivals/{id}/explain` returns explanation + `calculation_trace_id`
4. `/v3/api/provenance/root` returns trust root fields
5. `/v3/api/reliability/status` returns runtime + policy fields

## Report
- Output: `/Users/rohanbasnet14/Documents/Project Parva/reports/conformance_report.json`
- Pass criteria: all checks pass (`pass_rate = 100%`)
