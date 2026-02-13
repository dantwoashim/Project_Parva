# Trust and Provenance

Project Parva now publishes cryptographic provenance metadata with date responses.

## Components

- `dataset_hash`: SHA-256 digest over canonical dataset files.
- `rules_hash`: SHA-256 digest over festival rule files + engine config.
- `snapshot_id`: immutable snapshot record id (`snap_YYYYMMDDTHHMMSSZ`).
- `verify_url`: endpoint for independent verification.

## Snapshot Lifecycle

1. Generate/update festival snapshot (`backend/data/snapshot.json`) with:
   - `PYTHONPATH=backend python3 backend/tools/generate_snapshot.py`
2. Snapshot record is written to:
   - `backend/data/snapshots/<snapshot_id>.json`
3. Frozen festival snapshot copy is stored for Merkle proofs:
   - `backend/data/snapshots/<snapshot_id>.festival_snapshot.json`
4. Latest pointer is updated:
   - `backend/data/snapshots/latest.json`

## Verification Endpoints

- `GET /v2/api/provenance/root`
- `POST /v2/api/provenance/snapshot/create`
- `GET /v2/api/provenance/snapshot/{snapshot_id}/verify`
- `GET /v2/api/provenance/proof?festival={id}&year={year}&snapshot={snapshot_id}`
- `GET /v2/api/provenance/verify/{festival_id}?year={year}&snapshot={snapshot_id}`

## Local Verifier Script

Use the verifier script against any saved API response that includes `provenance`:

```bash
python3 scripts/verify_parva_response.py response.json --base http://localhost:8000
```

## Guarantees

- If dataset/rules do not change, hashes remain deterministic.
- Snapshot verification detects tampering in tracked files.
- Merkle proof verification detects festival-date changes in frozen snapshots.

## Limitations

- Merkle proofs verify inclusion in a specific frozen snapshot, not business correctness.
- Historical snapshots require retained snapshot files under `backend/data/snapshots/`.
