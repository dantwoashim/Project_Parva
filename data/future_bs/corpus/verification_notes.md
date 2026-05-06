# Future BS Month-Length Corpus Verification Notes

This corpus is intentionally source-labeled. It must not be described as a fully official
historical calendar corpus.

## Current Coverage

- Range: `2000-2099 BS`
- Structured official provenance accepted by the app: `2078-2083 BS`
- Archived official but not yet structured: `2076-2077 BS`
- Remaining rows: legacy static lookup table, retained as `third_party_reference` and
  `needs_review`

## Source Rules

- `official_verified`: structured official-source artifacts accepted in repository provenance.
- `approved_patro`: archived or approved calendar material, but not yet a fully accepted
  structured month-length extraction.
- `third_party_reference`: useful reference data, not official ground truth.
- `needs_review`: must not be used for financial-contract certainty without independent review.

## Product Claim Boundary

Parva may claim it is calibrated against a source-labeled historical corpus. Parva must not
claim the entire `2000-2099 BS` table is official. Future outputs are computed predictions,
not official publications.
