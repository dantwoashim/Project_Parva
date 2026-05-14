---
status: draft
tier: 2
lane: protocol
last_verified: 2026-05-14
owner: protocol-team
---

# Protocol Conformance

Parva Protocol conformance is currently alpha conformance for a protocol draft. It is intended to make public behavior reproducible and inspectable. It is not third-party certification and it does not create official calendar authority.

Compatibility levels:

- `parva_core`
- `parva_source_aware`
- `parva_trust`
- `parva_timegraph`
- `parva_rulelang`
- `parva_impact`
- `parva_agent_safe`
- `parva_offline`
- `parva_full`

A conformance report includes implementation name, protocol version, level, pass/fail status, test counts, test results, warnings, and report hash.

## What `parva_full` Checks

`parva_full` must be more than a smoke test. It checks:

- deterministic route-adjacent conversion behavior for a published validation case
- protocol metadata and claim boundary presence
- source registry readability
- public release manifest readability
- non-empty public trust log
- RuleLang schema presence
- preview offline bundle checksums for required contents
- Python and JavaScript SDK entrypoints
- protocol schema index coverage
- rejection of an invalid artifact

The public CI also runs a separate safety gate for OpenAPI exposure, public route profiles, unverified future conversion blocking, schema validation, and public text scans.

The CLI can also evaluate an explicit fixture artifact:

```bash
python scripts/parva_conformance.py --target local --level parva_core --artifact conformance/corpus/core/date_conversion.json
```

Invalid fixtures must fail with a structured report. This is intentional and proves the conformance runner does not pass every artifact by default.
