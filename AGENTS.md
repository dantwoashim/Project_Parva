# AGENTS.md - Project Parva Operating Instructions

These instructions apply to this repository unless a nested `AGENTS.md`
overrides them.

## Operating Standard

Complete the actual engineering objective. Do not stop at scaffolding,
placeholder files, optimistic documentation, or untested code.

A task is complete only when:

1. the code path works,
2. relevant tests pass or failures are documented,
3. generated artifacts exist and are non-empty,
4. examples match current APIs,
5. public claims match implementation,
6. remaining blockers are exact and actionable.

## Truth and Authority Boundaries

Never claim government authority, legal authority, tax authority, payroll
authority, banking authority, religious authority, official future-date
authority, official Panchanga authority, external certification, registry
acceptance, package publication, customers, or adoption unless repository
evidence proves it.

Future-sensitive outputs must remain review-aware. Panchanga outputs must remain
computed and method-docketed, not ritual final authority.

## Proof-System Rules

- Low-authority data must never become high-authority output.
- No sample source docket may appear in production proof paths.
- Proof-supported operations require replay verification, not just hash or shape
  checks.
- Public/stable proof routes need field provenance, boundary vectors, policy
  traces, and tamper tests.
- Static lookup mode must not serialize as source-backed authority.
- Method-backed Panchanga output must disclose ephemeris provider, location,
  timezone, ayanamsa, method dockets, and non-authority boundaries.

## Verification Loop

Use Python 3.11 and Node 20. Prefer focused tests first, then public gates.

Common commands:

```bash
py -3.11 scripts/release/check_public_claims.py
py -3.11 scripts/release/check_ceiling_depth_semantics.py
py -3.11 scripts/release/check_public_openapi_drift.py
py -3.11 -m pytest -q -m "not private_source and not wide_corpus and not research_artifact" --maxfail=20
py -3.11 scripts/release/verify_public.py
```

For local-kernel work:

```bash
cd packages/parva-local-kernel
npm install
npm test
```

Do not weaken checks to make a run pass.
