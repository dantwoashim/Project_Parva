# Project Parva Vision (Planned, Not Yet Complete)

Last updated: 2026-02-12

This document tracks future scope from the Master Plan. Items here are **planned** unless explicitly moved into `/docs/AS_BUILT.md`.

## Program Goal (12-Month Production-Grade Completion)
1. Normalize all APIs to a canonical response envelope.
2. Expand computed festival coverage to 300+ observances.
3. Deliver full frontend platform UX (explorer, panchanga, subscription flows).
4. Ship personal astrology modules (panchanga/muhurta/kundali).
5. Add production-grade community and AR layers.

## Planned Phases

### Phase 1: Contract Unification (v4)
- Canonical `data/meta` response envelope for every endpoint.
- v3 compatibility retained as LTS.
- v5 authority track baseline now started (`/v5/api/resolve`, `/v5/api/spec/conformance`).

### Phase 2: Frontend Platform Completion
- Multi-page app with routing, search/filter/sort, panchanga viewer, iCal subscription UI.
- Frontend test stack in CI.

### Phase 3: Festival + Site Expansion
- 300+ rules with provenance/confidence.
- 500+ mapped cultural sites and expanded region/tradition variants.

### Phase 4: Personal Modules
- Profile-driven personal panchanga.
- Muhurta recommendation engine.
- Basic kundali outputs (D1, D9, major dasha timeline).

### Phase 5: Community Layer
- Persistent check-ins, corrections, moderation workflow, abuse controls.

### Phase 6: AR/WebXR
- Temple overlay + sky-time integration with graceful fallbacks.

### Phase 7: Release Hardening
- External reproducibility package refresh.
- Security/reliability drills and v4 release dossier.

## Truthfulness Rule
- Completed claims must link to:
  - implementation path(s),
  - test evidence,
  - and release note/reference doc.
- Aspirational items remain in this file until promoted to `AS_BUILT`.
