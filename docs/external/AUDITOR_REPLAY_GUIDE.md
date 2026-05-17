# Auditor Replay Guide

1. Generate or inspect committed fixtures under `tests/fixtures/proof/`.
2. Verify backend replay with `tests/integration/test_shared_proof_fixtures.py`.
3. Verify local/offline replay with `packages/parva-local-kernel`.
4. Verify proof packs with `parva verify-proofpack <path>` when using the Python
   CLI from a repository checkout.
5. Verify Timepacks with `parva verify-timepack <path>`.

If a fixture, method docket, source docket, or ephemeris hash changes, replay
must be rerun. Hash consistency alone is not sufficient.
