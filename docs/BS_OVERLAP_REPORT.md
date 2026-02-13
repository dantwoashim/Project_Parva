# BS Overlap Report (Official vs Estimated)

This report compares sankranti-based estimated conversion against the official lookup table
for every day inside the official overlap window.

- Official range: `2070-2095 BS`
- Gregorian overlap: `2013-04-13` to `2039-04-14`
- Days compared: **9498**
- Matches: **4851**
- Mismatches: **4647**
- Match rate: **51.0739%**

## Interpretation

- Official conversion remains authoritative in-table.
- Estimated mode is useful for long-range extrapolation but not identical to committee tables.
- API confidence must therefore stay explicit: `official` in-range, `estimated` out-of-range.

## First 20 Mismatches

| Gregorian | Official BS | Estimated BS | Delta Days |
|---|---|---|---|
| 2013-04-13 | 2070-01-01 | 2069-12-30 | 0 |
| 2013-04-14 | 2070-01-02 | 2070-01-01 | -1 |
| 2013-04-15 | 2070-01-03 | 2070-01-02 | -1 |
| 2013-04-16 | 2070-01-04 | 2070-01-03 | -1 |
| 2013-04-17 | 2070-01-05 | 2070-01-04 | -1 |
| 2013-04-18 | 2070-01-06 | 2070-01-05 | -1 |
| 2013-04-19 | 2070-01-07 | 2070-01-06 | -1 |
| 2013-04-20 | 2070-01-08 | 2070-01-07 | -1 |
| 2013-04-21 | 2070-01-09 | 2070-01-08 | -1 |
| 2013-04-22 | 2070-01-10 | 2070-01-09 | -1 |
| 2013-04-23 | 2070-01-11 | 2070-01-10 | -1 |
| 2013-04-24 | 2070-01-12 | 2070-01-11 | -1 |
| 2013-04-25 | 2070-01-13 | 2070-01-12 | -1 |
| 2013-04-26 | 2070-01-14 | 2070-01-13 | -1 |
| 2013-04-27 | 2070-01-15 | 2070-01-14 | -1 |
| 2013-04-28 | 2070-01-16 | 2070-01-15 | -1 |
| 2013-04-29 | 2070-01-17 | 2070-01-16 | -1 |
| 2013-04-30 | 2070-01-18 | 2070-01-17 | -1 |
| 2013-05-01 | 2070-01-19 | 2070-01-18 | -1 |
| 2013-05-02 | 2070-01-20 | 2070-01-19 | -1 |

## Notes

- `delta_days` is measured by converting the estimated BS back to Gregorian and comparing with input date.
- Use this file together with `tests/fixtures/bs_overlap_comparison.json` in regression and contract docs.
