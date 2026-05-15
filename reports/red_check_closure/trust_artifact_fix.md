# Trust Artifact Fix

## Problem

The audit reported a stale hash for
`data/public/releases/parva-bs-public-demo.sources.json` and stale manifest /
hash-only signature checks.

## Fix

`scripts/release/regenerate_public_release_hashes.py` now validates every
manifest artifact path before hashing. It rejects:

- absolute paths
- directory traversal
- private source archive paths
- private Future-BS artifact paths
- local ephemeris paths
- credential or secret path tokens

This keeps deterministic hash regeneration from accepting private or local-only
artifact references.

## Tests

Added `tests/unit/release/test_regenerate_public_release_hashes.py` covering:

- absolute artifact path rejection
- private artifact storage rejection
- directory traversal rejection

## Evidence

- `python -m pytest tests/unit/release/test_regenerate_public_release_hashes.py tests/unit/release/test_verify_release.py -q`: 5 passed.
- `python scripts/release/regenerate_public_release_hashes.py --check`: pass.
- `python scripts/release/regenerate_public_release_hashes.py --write`: pass.
- `python scripts/parva_trust_verify.py`: pass.

The trust layer remains hash-only/alpha-signature preview; no real external
signing authority is claimed.

