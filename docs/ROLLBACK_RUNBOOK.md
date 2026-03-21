# Rollback Runbook

Use this guide when a Parva release candidate or fresh production deployment must be backed out.

## Immediate Stabilization

1. Stop new promotion activity.
2. Capture the failing build SHA, deployment URL, and the first visible symptom.
3. Preserve the current provenance snapshot, browser-smoke output, and release artifacts before redeploying.

## Rollback Decision Triggers

Rollback immediately if any of the following are true:

- public `/v3/api/*` responses regress or break contract expectations
- provenance attestation fails verification in the deployed environment
- festival or personal responses silently fall back without degraded-state metadata
- frontend build is live but high-traffic paths fail to render or trap users in broken dialogs
- release artifacts cannot be traced to a clean source archive

## Rollback Sequence

1. Redeploy the last known good artifact or Render release.
2. Re-run:
   - `/health/ready`
   - `/v3/api/calendar/today`
   - `/v3/api/personal/panchanga`
   - the main Today, Festivals, My Place, Saved, and Integrations frontend paths
3. Verify the restored build SHA and provenance snapshot match the intended rollback target.
4. Reopen traffic only after smoke checks pass.

## Aftercare

Record the rollback in the technical dossier with:

- incident start and rollback completion times
- failed candidate SHA
- restored SHA
- user-visible impact
- provenance/contract evidence captured during rollback
- follow-up owner for the blocked release
