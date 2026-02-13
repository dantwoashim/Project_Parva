# Uncertainty Specification (Year 3 M26)

## Objective
Expose calibrated uncertainty metadata on date outputs so clients can distinguish official certainty from modeled estimates.

## Response Shape
```json
{
  "uncertainty": {
    "level": "exact|confident|estimated|uncertain|degraded",
    "probability": 0.0,
    "interval_hours": 0.0,
    "calibration_data_size": 0,
    "methodology": "string",
    "notes": "optional",
    "boundary_proximity_minutes": 0.0
  }
}
```

## Level Semantics
- `exact`: official lookup or high-confidence astronomical mode.
- `confident`: reliable computed value with wider tolerance than exact.
- `estimated`: extrapolated mode (outside official lookup range).
- `uncertain`: boundary-sensitive or approximation-heavy case.
- `degraded`: fallback mode due to runtime/source limitations.

## Calibration Source
Artifact:
- `/Users/rohanbasnet14/Documents/Project Parva/reports/uncertainty_calibration.json`

Generator:
- `PYTHONPATH=backend python3 backend/tools/calibrate_uncertainty.py`

## Boundary-Sensitive Logic
For tithi:
- If proximity to nearest tithi boundary is <= 30 minutes, uncertainty is widened and downgraded to `uncertain`.
- Boundary proximity is estimated from tithi progress and average tithi duration (23.6h).

## Current Coverage
Uncertainty is attached to:
- `/v2/api/calendar/convert`
- `/v2/api/calendar/today`
- `/v2/api/calendar/tithi`
- `/v2/api/calendar/panchanga`
