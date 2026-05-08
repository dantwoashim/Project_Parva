# Future BS Methodology

Parva Future BS is a computational validation engine for BS month-length risk. It does not publish official future calendars. Public material describes methodology, source policy, and claim boundaries. Direct future values and operational audit outputs are private deployment surfaces.

## Architecture

```text
source-labeled corpus
  -> solar-ingress computation
  -> civil month-start rules
  -> calibrated ensemble
  -> probabilities and risk flags
  -> private comparison and schedule-risk review
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
8. Keep direct prediction artifacts private unless an authorized deployment explicitly exposes them.

## Current Ephemeris Position

Production builds download NASA NAIF `de440.bsp`, verify its published checksum, and expose it through `PARVA_JPL_DE440_KERNEL`. When that file is present, the future-BS solar-ingress path uses the JPL-backed adapter. Swiss Ephemeris and the built-in Moshier path remain fallback/cross-check layers. Normal API requests read precomputed prediction and solar-ingress cache artifacts instead of solving raw astronomy live.

## Backtesting

Supported modes:

- Holdout: train on one historical range and test a later range.
- Full replay: replay known years.
- Rolling validation: train up to year N and predict N+1.

Backtesting is a model-quality signal, not official certification.
