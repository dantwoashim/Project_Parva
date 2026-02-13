# BS Extended Range Validation

This report validates extended-range conversion behavior (diagnostic mode).

## Historical Samples

| Gregorian | BS | Roundtrip Δ (days) | Confidence |
|---|---|---:|---|
| 1900-01-01 | 1956-09-18 | 0 | estimated |
| 1943-04-14 | 2000-01-01 | 0 | estimated |
| 1950-01-01 | 2006-09-17 | 0 | estimated |
| 1975-06-15 | 2032-03-01 | 0 | estimated |
| 2000-01-01 | 2056-09-16 | 0 | estimated |

## Future Samples

| Gregorian | BS | Roundtrip Δ (days) | Confidence |
|---|---|---:|---|
| 2040-01-01 | 2096-09-16 | 0 | estimated |
| 2050-02-15 | 2106-11-02 | 0 | estimated |
| 2080-08-01 | 2137-04-17 | 0 | estimated |
| 2100-01-01 | 2156-09-16 | 0 | estimated |
| 2200-12-31 | 2257-09-13 | 0 | estimated |

## Notes

- Outside official range, results are intentionally marked `estimated`.
- Roundtrip deltas are expected to be small for estimated-mode consistency checks.
