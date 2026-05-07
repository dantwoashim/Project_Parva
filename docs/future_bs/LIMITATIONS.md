# Future BS Limitations

Parva Future BS is intentionally conservative about what it claims.

## Non-Official Status

Future predictions return `publication_status: not_official_publication`. They are computational outputs, not government calendar publications and not legal/tax final authority.

## Source Quality

Rows in the corpus are source-labeled. Only rows marked `official_verified` should be treated as structured official reference rows. Rows marked `approved_patro`, `third_party_reference`, or `needs_review` are useful for calibration and comparison, but require review before high-stakes use.

## Ephemeris Status

The JPL DE440 adapter requires an installed `.bsp` kernel. Cloud Run builds download and verify `de440s.bsp`; local development must run `scripts/download_jpl_kernel.py` or set `PARVA_JPL_DE440_KERNEL` manually. If the kernel is missing, the engine falls back to the available Swiss/Moshier-style path and labels results accordingly.

## Civil-Date Uncertainty

Solar ingress time alone does not fully decide the published civil month start. The engine tests multiple civil assignment rules and flags boundary-sensitive months. A near-boundary month can be technically plausible while still requiring human review.

## Financial Use

Loan and interest impact simulation estimates the consequences of a month-length mismatch. It does not decide contract language, regulatory treatment, tax handling, or final production adoption.
