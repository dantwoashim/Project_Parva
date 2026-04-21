# Runbook: Precompute Artifact Failure

## Signal

- production startup fails because required precomputed artifacts are missing
- readiness reports stale or missing precomputed data

## Immediate action

- verify the current artifact bundle is present
- regenerate artifacts if needed
- only set `PARVA_REQUIRE_PRECOMPUTED=false` intentionally and temporarily if the operator is knowingly accepting a degraded path

## Verification

- `GET /health/ready`
- public artifact listing and relevant route smoke checks
