# Year 1 Week 42 Status (Merkle Proof Integration)

## Completed
- Extended provenance routes with snapshot-aware proof workflow:
  - `/Users/rohanbasnet14/Documents/Project Parva/backend/app/provenance/routes.py`
- Added query-style proof endpoint:
  - `GET /v2/api/provenance/proof?festival={id}&year={year}&snapshot={snapshot_id}`
- Added snapshot endpoints:
  - `POST /v2/api/provenance/snapshot/create`
  - `GET /v2/api/provenance/snapshot/{snapshot_id}/verify`
- Updated Merkle root helper for snapshot-path support:
  - `/Users/rohanbasnet14/Documents/Project Parva/backend/app/calendar/merkle.py`

## Outcome
- Inclusion proofs can now be requested and verified against specific snapshot ids.
