# Scoring

Total score: 100.

| Category | Points |
| --- | ---: |
| Correctness | 40 |
| Source awareness | 20 |
| Uncertainty handling | 20 |
| Review gate behavior | 10 |
| Machine-readable structure | 10 |

Correctness checks expected outputs for stable public cases. Source awareness
checks source/confidence or equivalent evidence metadata. Uncertainty handling
checks unsupported and review-required behavior. Review gate behavior checks
that Future-BS cases are not treated as official exact predictions.

Runners should return a report even when individual tasks fail. A nonzero
process exit is reserved for blocked runner execution or an explicit
`--fail-under` threshold.
