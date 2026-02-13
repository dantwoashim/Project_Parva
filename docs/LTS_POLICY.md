# v3 LTS Policy

## Stability Promise
- `v3` is designated Long-Term Stable (LTS).
- No breaking response-shape changes in v3 without a major version bump (`v4`).

## Compatibility Rules
- Additive fields are allowed only when non-breaking and documented.
- Existing fields cannot be removed or type-changed in v3.
- Any proposed contract change must include:
  - migration note
  - schema diff
  - conformance/contract test updates

## Support Window
- v3 support window target: minimum 24 months from stabilization tag.

## Enforcement
- OpenAPI snapshot freeze checks in release workflow.
- Contract tests for versioned aliases and explainability traces.
