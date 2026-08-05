# Real-Tool Comparison: BS Conformance and Forecast Replay

Snapshot: 2026-08-05

## Historical BS Month Conformance

Each implementation was executed through its published BS-to-AD conversion surface. Month length was derived from consecutive month starts and compared with the same 72-case 2078-2083 fixture.

| Implementation | Version | Exact months | Accuracy |
| --- | --- | ---: | ---: |
| [Project Parva](https://github.com/dantwoashim/Project_Parva) | repository-main | 72/72 | 100.00% |
| [nepali-date-converter](https://www.npmjs.com/package/nepali-date-converter) | 3.4.0 | 72/72 | 100.00% |
| [@sonill/nepali-dates](https://www.npmjs.com/package/@sonill/nepali-dates) | 1.0.7 | 56/72 | 77.78% |
| [nepali-date-library](https://www.npmjs.com/package/nepali-date-library) | 1.1.15 | 72/72 | 100.00% |
| [@remotemerge/nepali-date-converter](https://www.npmjs.com/package/@remotemerge/nepali-date-converter) | 1.2.1 | 72/72 | 100.00% |

Historical conformance measures current lookup/conversion output. It does not test forecasting because every package already contains data for the target years.

Consumer calendar websites, including Hamro Patro and Nepali Patro, are outside the scored set. This benchmark admits only version-pinned public developer interfaces that can be replayed in CI, and this review did not identify a qualifying interface for either site.

## Chronological Forecast Replay

Parva: 72/72 exact month predictions (100.00%).

For each target year, Parva trained only through the previous year. The four conversion packages publish lookup tables rather than forecast methods, so they are not scored in this track.

## Market Review

No second product matching the full definition was found in the documented review scope.

The review found other location-aware Panchanga APIs and other Nepali date converters. The defensible distinction is the complete Nepal-focused combination, not an absolute claim that no astronomical Panchanga API exists.

## Reproduce

```bash
cd public-benchmark/competitors && npm ci --ignore-scripts
cd ../.. && py -3.11 public-benchmark/runners/run_competitor_comparison.py
```

The JSON artifact records package versions, per-month mismatches, the forecast replay split, and SHA-256 hashes for the fixture and runners.
