---
status: stable
tier: 1
lane: operations
last_verified: 2026-05-14
owner: platform-team
---

# Runbook: Release Rollback

## Trigger

- release candidate gates fail after deployment
- provenance, policy, or artifact outputs do not match the expected release

## Immediate action

- roll back to the previous known-good build
- restore the previous precomputed and provenance artifacts if the release changed them
- keep the corresponding source publication aligned with the rolled-back build

## Verification

- `GET /health/live`
- `GET /health/ready`
- `GET /source`
- representative `/v3/api/*` smoke routes
