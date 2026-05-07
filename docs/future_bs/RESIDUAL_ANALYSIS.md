# Future BS Residual Analysis

Generated: 2026-05-07T15:14:42.004931+00:00

## Scope

- Train range: 2000-2065 BS
- Test range: 2066-2083 BS
- Source policy: all_reference
- Model: parva_solar_statistical_stack_v1
- Method version: parva_solar_civil_accuracy_v6

## Month-Level Metrics

- Overall top-1 accuracy: 99.07%
- Green-zone accuracy: 100.0%
- Green-zone coverage: 85.19%
- Boundary cases flagged: 100.0%
- Ready for 99% claim: False

## Residual Clusters

- Mismatches by BS month: `{"11": 1, "12": 1}`
- Mismatches by ingress hour: `{"1": 1, "22": 1}`
- Mismatches by boundary distance: `{"gte_360_min": 2}`
- Mismatches by source type: `{"third_party_reference": 2}`
- Alternative rules that would have worked: `{"civil_decision_knn": 2}`

## Mismatch Table

| BS year | Month | Official | Predicted | Boundary | Rule | Alternative |
|---:|---:|---:|---:|---|---|---|
| 2066 | 11 | 29 | 30 | low | statistical_pattern | civil_decision_knn |
| 2066 | 12 | 31 | 30 | low | statistical_pattern | civil_decision_knn |


## Claim Boundary

This report is a technical evaluation artifact. It is not an official future Nepali calendar publication and must not be used to market a 99%+ claim unless the readiness flag is true on a source-strict official/printed benchmark.
