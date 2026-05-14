---
status: public-beta
tier: 1
lane: core
last_verified: 2026-05-14
owner: platform-team
---

# Runbook: Source Publication Missing

## Signal

- startup validation fails because `PARVA_SOURCE_URL` is missing
- `/source` is incorrect or unavailable

## Immediate action

- set `PARVA_SOURCE_URL` to the public repository or exact source archive for the deployed build
- verify that the URL is reachable and not `/source` itself

## Verification

- `GET /source`
- response headers include the expected source publication metadata
- `GET /health/ready`
