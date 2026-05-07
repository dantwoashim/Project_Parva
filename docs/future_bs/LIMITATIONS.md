# Future BS Limitations

Parva Future BS is intentionally conservative about what it claims.

## Non-Official Status

Future predictions return `publication_status: computed_prediction_not_official`. They are computational outputs, not government calendar publications and not legal/tax final authority.

## Source Quality

Rows in the corpus are source-labeled. Only rows marked `official_verified` should be treated as structured official reference rows. Rows marked `approved_patro`, `third_party_reference`, or `needs_review` are useful for calibration and comparison, but require review before high-stakes use.

The current source-strict official benchmark contains 72 month cases, below the
528 month cases needed for a defensible 40+ year accuracy claim. Parva therefore
blocks a 99%+ claim until more official/printed years are verified and the
green-zone benchmark passes.

## Ephemeris Status

The JPL DE440 adapter requires an installed `.bsp` kernel for live regeneration. Cloud Run builds download and verify `de440.bsp`; local development can run `scripts/download_jpl_kernel.py --kernel de440` or set `PARVA_JPL_DE440_KERNEL` manually. DE441 part kernels can be downloaded with `--kernel de441-part1` and `--kernel de441-part2` for cross-check work. Precomputed trusted artifacts may be served without live JPL regeneration.

## Civil-Date Uncertainty

Solar ingress time alone does not fully decide the published civil month start. The engine tests multiple civil assignment rules and flags boundary-sensitive months. A near-boundary month can be technically plausible while still requiring human review.

## Financial Use

Loan and interest impact simulation estimates the consequences of a month-length mismatch. It does not decide contract language, regulatory treatment, tax handling, or final production adoption.
