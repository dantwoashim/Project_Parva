# Project Parva As-Built (Evidence-Based)

Last updated: 2026-02-12

This document lists what is implemented and verifiable in the repository right now.

## Runtime + API
- FastAPI backend with versioned routes:
  - `/api/*` (compat), `/v2/api/*`, `/v3/api/*`, `/v4/api/*`, `/v5/api/*`
  - Source: `/Users/rohanbasnet14/Documents/Project Parva/backend/app/main.py`
- v3 LTS contract artifacts and docs:
  - `/Users/rohanbasnet14/Documents/Project Parva/docs/LTS_POLICY.md`
  - `/Users/rohanbasnet14/Documents/Project Parva/docs/MIGRATION_V2_V3.md`

## Calendar + Festival Engine
- Ephemeris-based tithi and panchanga, sankranti support, dual-mode BS conversion.
- Festival computation engine with lunar-month-aware rules and overrides.
- Evidence:
  - `/Users/rohanbasnet14/Documents/Project Parva/backend/app/calendar/`
  - `/Users/rohanbasnet14/Documents/Project Parva/backend/app/engine/`

## Provenance + Trust
- Snapshot hashes, Merkle/proof endpoints, transparency log routes.
- Evidence:
  - `/Users/rohanbasnet14/Documents/Project Parva/backend/app/provenance/`
  - `/Users/rohanbasnet14/Documents/Project Parva/docs/TRUST_AND_PROVENANCE.md`

## Reliability + Policy + Explainability
- Reliability status/SLO/playbook endpoints.
- Policy metadata endpoint and usage docs.
- Deterministic explain trace endpoints and UI panel.
- Evidence:
  - `/Users/rohanbasnet14/Documents/Project Parva/backend/app/api/reliability_routes.py`
  - `/Users/rohanbasnet14/Documents/Project Parva/backend/app/api/policy_routes.py`
  - `/Users/rohanbasnet14/Documents/Project Parva/backend/app/api/explain_routes.py`
  - `/Users/rohanbasnet14/Documents/Project Parva/frontend/src/components/Festival/ExplainPanel.jsx`

## Integrations
- iCal feed endpoints and webhook subscription/dispatch endpoints.
- Evidence:
  - `/Users/rohanbasnet14/Documents/Project Parva/backend/app/api/feed_routes.py`
  - `/Users/rohanbasnet14/Documents/Project Parva/backend/app/api/webhook_routes.py`

## SDKs (Productionized Baseline)
- Python SDK with typed envelope models and retry/backoff:
  - `/Users/rohanbasnet14/Documents/Project Parva/sdk/python/parva_sdk/`
- TypeScript SDK with typed envelope contract and packaging metadata:
  - `/Users/rohanbasnet14/Documents/Project Parva/sdk/typescript/`
- Go SDK with typed envelope structs, decoder helper, and `go.mod`:
  - `/Users/rohanbasnet14/Documents/Project Parva/sdk/go/`

## Validation Tooling
- Contract freeze checks, conformance runner, benchmark harness.
- Evidence:
  - `/Users/rohanbasnet14/Documents/Project Parva/scripts/release/check_contract_freeze.py`
  - `/Users/rohanbasnet14/Documents/Project Parva/scripts/spec/run_conformance_tests.py`
  - `/Users/rohanbasnet14/Documents/Project Parva/benchmark/harness.py`

## Authority Track Baseline (v5)
- Unified temporal resolve endpoint:
  - `/v5/api/resolve`
- Spec + conformance status endpoint:
  - `/v5/api/spec/conformance`
- Integration feed aliases:
  - `/v5/api/integrations/feeds/*`
- Trace integrity verification:
  - `/v5/api/provenance/verify/trace/{trace_id}`
- Core types and schemas:
  - `/Users/rohanbasnet14/Documents/Project Parva/backend/app/api/v5_types.py`
  - `/Users/rohanbasnet14/Documents/Project Parva/docs/spec/schemas/`
- Authority dashboard generation from CI artifacts:
  - `/Users/rohanbasnet14/Documents/Project Parva/scripts/generate_authority_dashboard.py`
  - `/Users/rohanbasnet14/Documents/Project Parva/docs/public_beta/authority_dashboard.md`

## Current Data Scope (As-Built)
- Festival entries in data file: 50
  - `/Users/rohanbasnet14/Documents/Project Parva/data/festivals/festivals.json`
- Canonical v4 rule catalog entries: 453 (computed + ingested provisional coverage)
  - `/Users/rohanbasnet14/Documents/Project Parva/data/festivals/festival_rules_v4.json`
- Temples mapped: 15
  - `/Users/rohanbasnet14/Documents/Project Parva/data/festivals/temples.json`
- v3 lunar rule coverage (computed set): 21
  - `/Users/rohanbasnet14/Documents/Project Parva/backend/app/calendar/festival_rules_v3.json`

## Known Gaps (Not Marked Complete)
- 300+ total rule catalog coverage achieved; most new entries are provisional and still require curation to reach "computed" quality.
- Personal Panchanga / Muhurta / Kundali modules not yet implemented.
- Community and AR/WebXR modules not yet implemented.
- Frontend has multi-page routing and tests, but still lacks auth/personalization and advanced partner workflows.
