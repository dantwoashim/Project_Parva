# Support Policy

Project Parva is an open-source project with best-effort community support.

## What is supported

- Build and run guidance for the current `main` branch
- The canonical `/v3/api/*` contract
- The Python SDK shipped from `sdk/python`
- The documented release and hygiene scripts in `scripts/release/`

## What is not guaranteed

- SLA-backed response times
- Private support channels
- Support for experimental alias tracks
- Long-term support for proof-of-concept utilities or lab surfaces
- Compatibility guarantees for unpublished internal/admin workflows

## Compatibility posture

- `/v3/api/*` is the only public API surface intended for new integrations.
- `/api/*` is maintained as a legacy alias, not a strategic long-term target.
- Experimental tracks can change or disappear without the deprecation window expected for `v3`.

## Triage priorities

1. Security or data-integrity regressions
2. Public `v3` contract regressions
3. Clean-clone build or release-gate failures
4. Documentation drift
5. UX and feature requests
