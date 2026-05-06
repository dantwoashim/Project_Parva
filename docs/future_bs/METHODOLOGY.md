# Future BS Methodology

Parva Future BS is a computational validation engine for BS month-length risk. It does not publish official future calendars. It produces reproducible, source-labeled predictions that can be compared against internal sheets and reviewed before financial use.

## Architecture

```text
source-labeled corpus
  -> solar-ingress computation
  -> civil month-start rules
  -> calibrated ensemble
  -> probabilities and risk flags
  -> external comparison
  -> loan-impact simulation
```

## Corpus

The corpus lives in `data/future_bs/corpus/verified_month_lengths.csv`.

Each year carries:

- `source_type`
- `source_reference`
- `verification_status`

The current corpus deliberately separates structured official rows from archived, third-party, and review-needed rows. Do not flatten these into one “official” label.

## Prediction Flow

For each future BS year:

1. Estimate the relevant Gregorian year window.
2. Compute solar ingress events for sidereal sign boundaries.
3. Convert ingress moments to Nepal civil time.
4. Apply multiple civil date assignment rules.
5. Derive month lengths from consecutive month-start dates.
6. Combine computational outputs with a weak legacy-cycle fallback.
7. Assign probabilities, confidence, and risk flags.
8. Serve the result from immutable precomputed prediction files.

## Current Ephemeris Position

The architecture includes JPL DE440 as a registered target, Swiss Ephemeris as the active cross-check path, and Moshier-style fallback. DE440 is not claimed active unless a JPL kernel is configured through deployment settings.

## Backtesting

Supported modes:

- Holdout: train on one historical range and test a later range.
- Full replay: replay known years.
- Rolling validation: train up to year N and predict N+1.

Backtesting is a model-quality signal, not official certification.
