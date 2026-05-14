---
status: draft
tier: 2
lane: protocol
last_verified: 2026-05-14
owner: protocol-team
---

# Conformance Program

Status: alpha self-attested conformance for a protocol draft.

The Phase 10 conformance program makes Project Parva behavior reproducible for
reviewers without claiming certification. The reference runner is
`python scripts/parva_conformance.py`.

## Scope

The program covers:

- public BS to AD conversion behavior
- protocol metadata and draft status
- public source registry boundaries
- release manifest and trust-log readability
- TimeGraph traceability
- RuleLang safe execution boundaries
- impact dependency extraction
- agent-safe review gates
- unsigned offline bundle checksums
- invalid fixture rejection

The program excludes private source archives, private client data, unpublished
future official calendars, legal conclusions, and production signature authority.

## Required Commands

```bash
python scripts/parva_conformance.py --target local --level parva_core
python scripts/parva_conformance.py --target local --level full
python scripts/parva_conformance.py --target local --level full --output reports/compatibility/project-parva-reference-full.json
```

The output report includes implementation name, protocol version, compatibility
level, test counts, per-test results, limitations, public/private data policy,
generation time, and report hash.

## Fixture Inventory

Phase 10 adds public valid and invalid fixtures for source-aware metadata, trust,
TimeGraph, RuleLang, impact, agent-safe, and offline bundle behavior. Invalid
fixtures are deliberate and prove the runner does not pass every artifact by
default.
