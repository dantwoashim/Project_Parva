# Reliability

## Health endpoints

- `/health/live`: process is running
- `/health/ready`: configuration and required dependencies are available
- `/health/startup`: startup validation completed

## Startup validation

Startup fails fast when dangerous combinations are enabled without required
backing configuration.

Current checks:

- experimental routes in production require `PARVA_ALLOW_EXPERIMENTAL_IN_PROD=true`
- webhook enablement is rejected because webhooks are not shipped in this build
- frontend serving in production requires the configured frontend dist directory to contain `index.html`

## Incident playbooks

For beta intake, severity classification, and support routing, use
`docs/CLOSED_BETA_OPERATIONS.md` alongside these technical playbooks.

### `ephemeris_unavailable`

- keep responses up with degraded metadata only if cache artifacts exist
- inspect `/api/reliability/status`
- verify the runtime ephemeris mode and release version in logs

### `cache_artifact_missing`

- regenerate with `python scripts/precompute/precompute_all.py`
- verify with `/api/public/artifacts/manifest`
- confirm `/health/ready` before routing traffic

### `source_outage`

- keep the public stateless read profile online
- avoid enabling experimental or mutable features
- attach discrepancy notes to the release dossier if outputs change
