# PTS-001 Date Representation

## Data model

BS and AD dates use ISO-like `YYYY-MM-DD` strings with explicit calendar labels where ambiguity is possible.

## Required fields

- `calendar`
- `date`

## Validation

Implementations must reject invalid BS month and day values and must disclose supported ranges.

## Boundary

Date conversion output is computational infrastructure. It is not legal authority.
