# Technical Appendix

The pilot release should include:

- `release.json` for release id, status, source metadata, supported ranges, and
  claim boundaries.
- `holidays.csv` for holiday rows with source ids and review flags.
- `festivals.json` for festival rows with authority and source fields.
- `panchanga-summary.json` for computed or published panchanga summaries with
  method metadata.
- `source-metadata.json` for source ids, tiers, evidence requirements, and
  retrieval metadata.
- `checksums.txt` for deterministic file verification.
- `verification/verify_release.py` for offline checksum verification.

All files should preserve:

- `source_tier`,
- `confidence`,
- `claim_boundary`,
- `review_required`,
- `not_authority`,
- `release_id`.

Private source archives, local paths, credentials, and unsupported exact
Future-BS predictions must not be included in the public release.
