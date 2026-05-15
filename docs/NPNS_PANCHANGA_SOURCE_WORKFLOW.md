---
status: public-beta
tier: 1
lane: core
last_verified: 2026-05-14
owner: platform-team
---

# NPNS Panchanga Source Workflow

Status: authority boundary and workflow scaffold.

Parva may digitize, cross-check, and compute panchanga metadata, but it is not NPNS, a publisher, a priestly authority, legal authority, or official civil authority.

## Required Public Language

Any NPNS or panchanga-backed output must say:

- source remains NPNS, publisher, or named authority
- Parva supports digitization, verification, traceability, and comparison
- calculated panchanga output has method metadata
- local tradition and authority-specific interpretation can differ
- legal, civil, religious, payroll, banking-contract, or regulatory decisions require explicit human review

## Workflow

1. Acquire the NPNS or publisher source with redistribution review.
2. Record source metadata: source id, source name, source tier, publisher/authority, year, URL or retained filename, checksum, reviewer, and retrieval date.
3. Extract date, tithi, nakshatra, yoga, karana, sunrise/sunset, festival, and note fields into a draft machine-readable table.
4. Mark extracted rows as `printed_verified`, `semi_official`, `publisher_reference`, or `public_witness` unless the source authority qualifies for `official`.
5. Record calculation method metadata for computed panchanga values.
6. Compare extracted rows against the calculation engine.
7. Classify conflicts as source conflict, calculation model issue, timezone/location issue, or extraction issue.
8. Generate review queue rows for conflicts.
9. Publish only public-safe derived rows and metadata.
10. Rebuild release hashes and verify trust artifacts.

## Conflict Policy

Official or reviewed source rows override calculated rows for public source-aware interpretation within their declared scope. Calculated rows can explain method output, but they do not become official publication.

Fixture-only panchanga data must stay in tests or conformance artifacts and must not support public quality claims.

