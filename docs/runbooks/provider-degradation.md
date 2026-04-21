# Runbook: Provider Degradation

## Signal

- place search latency or failures spike
- logs or route results show remote geocoder degradation

## Immediate action

- confirm the configured provider policy
- if running `acknowledged_remote`, verify upstream health and time budgets
- if privacy or reliability posture has changed, move the deployment to `offline_only`

## Verification

- test a known offline place query
- test a remote-dependent place query only if the deployment intentionally permits it
- confirm `/health/ready` and user-facing place routes behave as expected
