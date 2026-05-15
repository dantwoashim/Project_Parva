---
status: stable
audience: developer
---

# API Versioning and Deprecation

Project Parva uses route versions to separate stable infrastructure from preview
and research boundaries.

| Version | Meaning | Public posture |
| --- | --- | --- |
| `v3` | Stable/core canonical API | Default for SDKs and quickstarts |
| `v4` | Public preview or metadata-only research capability surfaces | Must be labeled preview or capability-only |
| `v5` | Model-risk, research, or explicit preview surfaces | Not stable; exact outputs require private gates |
| `v2` | Deprecated compatibility | Compatibility only; do not use in new SDK defaults |

Every public route should be mapped in `config/route-maturity.yaml` with a lane,
maturity, exposure rule, and claim boundary. OpenAPI tags must not make research
routes look stable. SDK defaults must use `/v3/api` unless a method is explicitly
named as a public-preview capability helper.

Deprecation rule:

1. Keep compatibility aliases only while documented.
2. Add replacement route, maturity lane, and sunset note.
3. Keep public OpenAPI and docs link checks green.
4. Do not remove behavior without contract tests or a migration note.

Public docs and SDK examples must not imply that v4 or v5 are stable exact
Future-BS APIs. Public v4/v5 capability routes may describe research posture,
but exact unsupported future outputs require private gates and remain
`computed_prediction_not_official`.
