---
status: draft
tier: 2
lane: protocol
last_verified: 2026-05-14
owner: protocol-team
---

# Parva Protocol Draft

Status: protocol draft, reference implementation.

Parva Protocol defines a draft interoperability layer for programmable,
verifiable, auditable Nepali time. The current public draft covers date
conversion metadata, source-aware records, release manifests, trust logs,
TimeGraph traces, RuleLang execution metadata, impact simulation, agent-safe
tooling, hash-only preview credentials, and unsigned preview offline bundles.

This document is not an authority claim. The protocol draft does not claim
government endorsement, legal authority, production signature authority, W3C
standard status, or third-party certification.

## Version

- Protocol version: `parva-protocol-0.1.0`
- Compatibility status: alpha conformance
- Reference implementation: Project Parva local public artifacts
- Data mode: public artifacts only

## Public Boundary

Public compatibility can use checked-in public release artifacts, public source
metadata, public schemas, public SDK files, and synthetic negative fixtures. It
must not require private source archives, client artifacts, research-only exact
future vectors, or unpublished official data.

Hash-only preview credentials prove local content integrity against the reference
implementation. They are not production digital signatures. Offline bundles are
unsigned previews and must be verified by checksum before use.

## Compatibility Levels

- `parva_core`: conversion behavior, protocol metadata, predictable errors
- `parva_source_aware`: source tiers, warnings, and claim boundaries
- `parva_trust`: manifests, hashes, trust logs, and release pinning
- `parva_timegraph`: traceable facts and relationships
- `parva_rulelang`: safe public rule validation and execution traces
- `parva_impact`: dependency extraction and impact summaries
- `parva_agent_safe`: deterministic tools and human-review gates
- `parva_offline`: local bundle checksums and private-data exclusion
- `parva_full`: aggregate alpha conformance across public levels

## Required Implementation Behavior

Implementations should return explicit limitations, claim boundaries, warnings,
compatibility level, protocol version, and generated report hashes. Negative
fixtures must fail. Compatibility must remain self-attested until independent
governance or external review exists.
