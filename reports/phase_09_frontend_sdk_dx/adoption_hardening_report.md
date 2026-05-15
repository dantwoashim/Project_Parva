# Adoption Hardening Report

Status: public generated artifact.

Wave 1 strengthened the first developer path around public-safe adoption:

- Quickstart now covers conversion, validation, holiday/observance lookup,
  working-day support, fiscal-year lookup, festival lookup, panchanga summary,
  source/confidence metadata, review-required behavior, unsupported Future-BS
  behavior, and retry/rate-limit handling.
- SDK strategy names `packages/parva-python` and `packages/parva-js` as the
  canonical SDKs and keeps `sdk/python` as compatibility scaffolding.
- API versioning distinguishes stable v3 from preview/research v4 and
  model-risk/research v5.
- SDK READMEs now preserve review and claim-boundary behavior.

Remaining SDK gap: named holiday, festival-detail, and panchanga helpers are
not yet promoted in both canonical SDKs. REST examples remain the public-safe
path for those calls.
