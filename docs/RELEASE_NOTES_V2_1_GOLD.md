# Release Notes — v2.1.0-gold

## Highlights
- Completed Year-1 Week 40–48 execution set.
- Added provenance snapshot hashing and verification endpoints.
- Added query-style Merkle proof endpoint for easier external verification.
- Added response-level provenance metadata for date-bearing endpoints.
- Added benchmark package with one-command reproducible run.
- Added technical report, verification dossier, and retrospective docs.

## API Additions
- `POST /v2/api/provenance/snapshot/create`
- `GET /v2/api/provenance/snapshot/{snapshot_id}/verify`
- `GET /v2/api/provenance/proof?festival={id}&year={year}&snapshot={snapshot_id}`

## Tooling Additions
- `scripts/verify_parva_response.py`
- `benchmark/run_benchmark.sh`

## Docs Added
- `docs/TRUST_AND_PROVENANCE.md`
- `docs/NEPAL_GOLD_TECHNICAL_REPORT.md`
- `docs/VERIFICATION_DOSSIER_2027.md`
- `docs/YEAR_1_RETROSPECTIVE.md`
