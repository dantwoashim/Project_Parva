# Product And Architecture Statement

Project Parva should be treated as two related deliverables with different maturity levels.

## Stable core platform

The stable core is the canonical `/v3/api/*` platform:

- temporal computation engines
- provenance and transparency surfaces
- route policy and access metadata
- reliability and degraded-state reporting
- public artifacts and release traceability

This is the primary production commitment.

## Preview and experimental surfaces

These remain outside the stable compatibility promise:

- `/v2`, `/v4`, `/v5` experimental aliases
- preview/admin overlays
- lab routes and dispute-analysis surfaces

They can stay public, but they must remain mechanically separable from the stable `/v3` core.

## Reference frontend

The React frontend is a public reference beta:

- it demonstrates the API and trust model
- it is maintained and tested
- it is not the same thing as a fully productized consumer application

If the project later adds real account/sync/member-state workflows, that work should be treated as a separate productization track, not assumed by default.
