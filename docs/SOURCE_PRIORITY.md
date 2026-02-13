# Source Priority Policy

When multiple sources disagree for the same festival/year, Parva resolves in this order:

1. `ground_truth_overrides` (manually curated authoritative corrections)
2. `moha_official` (Ministry of Home Affairs holiday publication)
3. `rashtriya_panchang` (Calendar Determination Committee publication)
4. `computed_ephemeris` (engine-calculated date)
5. `ocr_extracted` (machine-extracted data pending manual verification)

## Why this order
- User-facing correctness is prioritized over pure algorithmic output.
- Published official records win over inferred results.
- OCR is helpful for coverage but must not silently override trusted data.

## Tie-break notes
- If two official sources differ, Parva records both in discrepancy logs and prefers MoHA for holiday APIs.
- Region-specific variants are returned as variants in future API versions, not silently overwritten.
