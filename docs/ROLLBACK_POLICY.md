---
status: stable
tier: 1
lane: operations
last_verified: 2026-05-14
owner: platform-team
---

# Rollback Policy

Rollback is required when a deployment damages stable public correctness,
availability, public/private boundaries, or trust artifact integrity.

## Rollback Triggers

| Trigger | Action |
| --- | --- |
| Stable public route sustained 5xx | Roll back service image or platform release. |
| Public route exposes private Future-BS, source, customer, or credential data | Roll back immediately and rotate any exposed secrets. |
| Trust or release artifact hash mismatch | Roll back application and restore the matching artifact set. |
| Readiness fails after deploy | Roll back unless a documented warmup period explains it. |
| p95 budget breach on stable core routes | Roll back or disable the release path if breach is severe and sustained. |

## Render

1. Open the Render service deployment history.
2. Redeploy the last known good deploy.
3. Confirm environment variables still match the target profile.
4. Run deployment smoke.
5. Run trust verification if release artifacts changed.

## Cloud Run

1. Identify the previous revision.
2. Shift traffic back to the previous revision.
3. Confirm the previous revision uses compatible environment variables.
4. Run deployment smoke.
5. Keep the failed revision for log review until the incident is closed.

## Docker

1. Pull or retag the last known good image.
2. Restore the matching precomputed artifacts and public release files.
3. Start the container with the previous environment profile.
4. Run `/health/ready`, backend smoke, and deployment smoke.

## Trust Artifact Rollback

Application rollback must not serve a mismatched release manifest. If data
release artifacts changed, restore:

- `data/public/releases/*`
- `data/public/transparency-log/*`
- generated OpenAPI/profile artifacts tied to the release
- precomputed public artifacts if the release references them

Then run:

```bash
python scripts/parva_trust_verify.py
python tools/validate_schemas.py
python scripts/parva_protocol_verify.py
```

## Post-Rollback Review

Record:

- failed deploy id or image tag
- rollback target
- failed checks
- smoke command output
- data artifact compatibility decision
- follow-up owner
