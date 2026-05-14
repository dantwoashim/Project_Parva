# Phase 04 Backlog For Later Phases

Status: Phase 04 observations only.

The items below were observed while implementing maturity lanes. They belong to
later hardening, SRE, SDK, or model-improvement phases and were not implemented
as Phase 04 work.

## Phase 05 Or Later Security And Operations

- Billing, API-key, webhook, and admin routes need deeper production hardening
  beyond maturity classification.
- Rate-limit, Redis, Postgres, webhook validation, and production secrets
  posture should be verified in the dedicated security/SRE phase.
- Provenance mutation and billing mutation controls should receive dedicated
  abuse-case tests.

## Later Frontend And SDK Refinement

- The public app shell is now capability-aware, but direct URL route fallbacks
  still render pages even when a backend capability is unavailable. A later UX
  pass can add profile-aware unavailable states per route.
- SDK preview and draft helpers remain top-level compatibility methods. A later
  major SDK version can move these under explicit preview and draft namespaces.

## Later Future-BS Research

- Exact future-BS predictions, residual analysis, and model-run artifacts remain
  private. Any later public claim upgrade requires fresh source policy,
  validation, and leakage checks.
- Further model accuracy work should continue to separate strict official
  evidence from broader all-reference stress tests.

